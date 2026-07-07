from pathlib import Path
from typing import Optional, Dict, Any
import os
import re

try:
    from ...config import (
        logger,
        NAMING_TEMPLATE,
        Audio,
        Subtitles,
        build_provider_attempt_order,
    )
    from ...models.common import ProviderData, clean_title
    from ...models.common.common import (
        download as episode_download,
        watch as episode_watch,
        syncplay as episode_syncplay,
    )
    from .get_iplayer_api import GetIPlayerAPI
except ImportError:
    from aniworld.config import (
        logger,
        NAMING_TEMPLATE,
        Audio,
        Subtitles,
        build_provider_attempt_order,
    )
    from aniworld.models.common import ProviderData, clean_title
    from aniworld.models.common.common import (
        download as episode_download,
        watch as episode_watch,
        syncplay as episode_syncplay,
    )
    from .get_iplayer_api import GetIPlayerAPI


class BBCiPlayerEpisode:
    def __init__(
        self,
        pid: str = None,
        title: str = None,
        channel: str = None,
        episode_info: Optional[str] = None,
        description: Optional[str] = None,
        content_type: str = "tv",
        url: str = None,
    ):
        if url and pid is None:
            match = re.match(r"^bbc-iplayer://(?:tv|radio)/([a-z0-9]+)(?:\?.*)?$", url, re.IGNORECASE)
            if match:
                pid = match.group(1)
                content_type = "tv" if "://tv/" in url else "radio"
        
        self.pid = pid or "unknown"
        self.title = title or "Unknown"
        self.channel = channel or "Unknown"
        self.episode_info = episode_info
        self.description = description
        self.content_type = content_type
        
        self.api = GetIPlayerAPI()
        
        self._provider_data = None
        self._selected_provider = None
        self._selected_path = None

    @property
    def title_de(self) -> str:
        return self.title

    @property
    def title_en(self) -> str:
        return self.title

    @property
    def provider_data(self) -> ProviderData:
        if self._provider_data is None:
            self._provider_data = ProviderData()
            
            quality_options = {
                (Audio.ENGLISH, Subtitles.NONE): {
                    "GetIPlayer": f"bbc-iplayer://{self.content_type}/{self.pid}"
                }
            }
            
            if self.content_type == "tv":
                quality_options[(Audio.ENGLISH, Subtitles.ENGLISH)] = {
                    "GetIPlayer": f"bbc-iplayer://{self.content_type}/{self.pid}?subtitles=true"
                }
            
            for lang_sub, providers in quality_options.items():
                for provider_name, url in providers.items():
                    self._provider_data.add(lang_sub, provider_name, url)
        
        return self._provider_data

    @property
    def stream_url(self) -> Optional[str]:
        return f"bbc-iplayer://{self.content_type}/{self.pid}"

    @property
    def redirect_url(self) -> Optional[str]:
        return self.stream_url

    @property
    def is_downloaded(self) -> bool:
        if not self._selected_path:
            return False
        path = Path(self._selected_path)
        return path.exists()

    @property
    def selected_provider(self) -> Optional[str]:
        return self._selected_provider

    @selected_provider.setter
    def selected_provider(self, value: str):
        self._selected_provider = value

    @property
    def selected_path(self) -> Optional[str]:
        return self._selected_path

    @selected_path.setter
    def selected_path(self, value: str):
        self._selected_path = value

    def download(self, path: Optional[str] = None) -> bool:
        try:
            quality = "hd,sd,web,mobile"
            subtitles = "subtitles=true" in self.stream_url if self.stream_url else False
            
            output_dir = path or str(Path.home() / "Downloads")
            
            logger.info(f"Starting BBC iPlayer download for PID: {self.pid}")
            success = self.api.download(
                self.pid,
                quality=quality,
                subtitles=subtitles,
                output_dir=output_dir
            )
            
            if success:
                logger.info(f"Successfully downloaded {self.title}")
            else:
                logger.error(f"Failed to download {self.title}")
            
            return success
        except Exception as e:
            logger.error(f"Error downloading BBC iPlayer episode: {e}")
            return False

    def watch(
        self,
        player: str = "mpv",
        **kwargs
    ) -> bool:
        try:
            logger.info(f"Opening BBC iPlayer episode in {player}: {self.title}")
            
            url = f"https://www.bbc.co.uk/iplayer/episode/{self.pid}"
            
            return episode_watch(url, player=player, **kwargs)
        except Exception as e:
            logger.error(f"Error watching BBC iPlayer episode: {e}")
            return False

    def syncplay(self, **kwargs) -> bool:
        try:
            logger.info(f"Starting Syncplay for BBC iPlayer episode: {self.title}")
            
            url = f"https://www.bbc.co.uk/iplayer/episode/{self.pid}"
            
            return episode_syncplay(url, **kwargs)
        except Exception as e:
            logger.error(f"Error starting Syncplay for BBC iPlayer episode: {e}")
            return False

    def __repr__(self) -> str:
        return (
            f"BBCiPlayerEpisode(pid={self.pid}, title={self.title}, "
            f"channel={self.channel}, episode_info={self.episode_info})"
        )
