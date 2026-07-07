import json
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from ...config import logger
except ImportError:
    from aniworld.config import logger


class GetIPlayerAPI:
    def __init__(self, get_iplayer_path: Optional[str] = None):
        self.get_iplayer_path = get_iplayer_path or self._find_get_iplayer()
        if not self.get_iplayer_path:
            raise RuntimeError(
                "get_iplayer not found. Please install get_iplayer or provide its path."
            )

    @staticmethod
    def _find_get_iplayer() -> Optional[str]:
        common_paths = [
            Path("/usr/bin/get_iplayer"),
            Path("/usr/local/bin/get_iplayer"),
            Path("/opt/homebrew/bin/get_iplayer"),
        ]
        
        for path in common_paths:
            if path.exists() and path.is_file():
                return str(path)
        
        try:
            result = subprocess.run(
                ["which", "get_iplayer"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return None

    def search_tv(self, keyword: str, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._search(keyword, "tv", channel)

    def search_radio(self, keyword: str, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._search(keyword, "radio", channel)

    def _search(self, keyword: str, content_type: str = "tv", channel: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            cmd = [self.get_iplayer_path, f"--type={content_type}", keyword]
            if channel:
                cmd.insert(2, f"--channel={channel}")
            
            logger.debug(f"Running get_iplayer search: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.warning(f"get_iplayer search failed: {result.stderr}")
                return []
            
            programmes = []
            for line in result.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                
                programme = self._parse_search_line(line)
                if programme:
                    programmes.append(programme)
            
            return programmes
        except subprocess.TimeoutExpired:
            logger.error(f"get_iplayer search timeout for keyword: {keyword}")
            return []
        except Exception as e:
            logger.error(f"Error searching with get_iplayer: {e}")
            return []

    @staticmethod
    def _parse_search_line(line: str) -> Optional[Dict[str, Any]]:
        try:
            match = re.match(
                r'^(\d+):\s+(.+?),\s+(.+?),\s+([a-z0-9]+)$',
                line.strip()
            )
            if match:
                index, name_episode, channel, pid = match.groups()
                
                title = name_episode.split(' - ')[0] if ' - ' in name_episode else name_episode
                episode_info = name_episode.split(' - ')[1] if ' - ' in name_episode else None
                
                return {
                    'index': int(index),
                    'title': title.strip(),
                    'episode': episode_info.strip() if episode_info else None,
                    'channel': channel.strip(),
                    'pid': pid.strip(),
                    'name_episode': name_episode.strip(),
                }
        except Exception as e:
            logger.debug(f"Could not parse search line: {line}. Error: {e}")
        
        return None

    def get_programme_info(self, pid: str) -> Optional[Dict[str, Any]]:
        try:
            cmd = [self.get_iplayer_path, f"--pid={pid}", "--long"]
            
            logger.debug(f"Getting programme info for PID: {pid}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Could not get programme info for {pid}")
                return None
            
            output = result.stdout.strip()
            if not output:
                return None
            
            lines = output.split('\n')
            if len(lines) < 1:
                return None
            
            programme = self._parse_search_line(lines[0])
            
            if programme and len(lines) > 1:
                description = '\n'.join(lines[1:])
                programme['description'] = description
            
            return programme
        except Exception as e:
            logger.error(f"Error getting programme info for {pid}: {e}")
            return None

    def download(
        self,
        pid: str,
        quality: str = "best",
        subtitles: bool = False,
        output_dir: str = None,
    ) -> bool:
        try:
            cmd = [self.get_iplayer_path, f"--pid={pid}", f"--tv-quality={quality}"]
            
            if subtitles:
                cmd.append("--subtitles")
            
            if output_dir:
                cmd.extend(["-o", output_dir])
            
            logger.debug(f"Starting get_iplayer download: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                timeout=3600,
            )
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.error(f"get_iplayer download timeout for PID: {pid}")
            return False
        except Exception as e:
            logger.error(f"Error downloading with get_iplayer: {e}")
            return False

    def list_channels(self, content_type: str = "tv") -> List[str]:
        try:
            cmd = [self.get_iplayer_path, f"--type={content_type}", "--list-channels"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            channels = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return channels
        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            return []
