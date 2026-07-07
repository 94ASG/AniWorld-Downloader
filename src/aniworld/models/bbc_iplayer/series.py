from typing import List, Optional, Dict, Any
import re

try:
    from ...config import logger
    from .get_iplayer_api import GetIPlayerAPI
    from .episode import BBCiPlayerEpisode
except ImportError:
    from aniworld.config import logger
    from .get_iplayer_api import GetIPlayerAPI
    from .episode import BBCiPlayerEpisode


class BBCiPlayerSeries:
    def __init__(self, url: str = None, pid: str = None, content_type: str = "tv"):
        if url and pid is None:
            match = re.match(r"^bbc-iplayer://(?:tv|radio)/([a-z0-9]+)(?:\?.*)?$", url, re.IGNORECASE)
            if match:
                pid = match.group(1)
                content_type = "tv" if "://tv/" in url else "radio"
        
        self.pid = pid or "unknown"
        self.url = url or f"bbc-iplayer://{content_type}/{self.pid}"
        self.content_type = content_type
        self.api = GetIPlayerAPI()
        
        self._info = None
        self._episodes = None
    
    def _load_info(self):
        if self._info is None:
            self._info = self.api.get_programme_info(self.pid)
    
    @property
    def title(self) -> str:
        self._load_info()
        if self._info:
            return self._info.get('title', 'Unknown')
        return 'Unknown'
    
    @property
    def description(self) -> Optional[str]:
        self._load_info()
        if self._info:
            return self._info.get('description')
        return None
    
    @property
    def channel(self) -> Optional[str]:
        self._load_info()
        if self._info:
            return self._info.get('channel')
        return None
    
    @property
    def genres(self) -> List[str]:
        return []
    
    @property
    def release_year(self) -> Optional[int]:
        return None
    
    @property
    def poster_url(self) -> Optional[str]:
        return None
    
    @property
    def directors(self) -> List[str]:
        return []
    
    @property
    def actors(self) -> List[str]:
        return []
    
    @property
    def producer(self) -> Optional[str]:
        return None
    
    @property
    def country(self) -> Optional[str]:
        return None
    
    @property
    def age_rating(self) -> Optional[str]:
        return None
    
    @property
    def seasons(self) -> List:
        return [BBCiPlayerSeason(self)]
    
    @property
    def season_count(self) -> int:
        return 1
    
    def download(self, path: Optional[str] = None) -> bool:
        logger.info(f"Starting download for BBC iPlayer series: {self.title}")
        
        if self._episodes is None:
            self._load_episodes()
        
        success_count = 0
        for episode in self._episodes:
            if episode.download(path):
                success_count += 1
        
        logger.info(f"Downloaded {success_count}/{len(self._episodes)} episodes")
        return success_count == len(self._episodes)
    
    def watch(self, player: str = "mpv", **kwargs) -> bool:
        logger.info(f"Opening BBC iPlayer series in {player}: {self.title}")
        
        if self._episodes is None:
            self._load_episodes()
        
        if self._episodes:
            return self._episodes[0].watch(player=player, **kwargs)
        
        return False
    
    def syncplay(self, **kwargs) -> bool:
        logger.info(f"Starting Syncplay for BBC iPlayer series: {self.title}")
        
        if self._episodes is None:
            self._load_episodes()
        
        if self._episodes:
            return self._episodes[0].syncplay(**kwargs)
        
        return False
    
    def _load_episodes(self):
        if self._episodes is None:
            self._episodes = []
            self._load_info()
            
            if self._info:
                episode = BBCiPlayerEpisode(
                    pid=self.pid,
                    title=self._info.get('title', 'Unknown'),
                    channel=self._info.get('channel', 'Unknown'),
                    episode_info=self._info.get('episode'),
                    description=self._info.get('description'),
                    content_type=self.content_type,
                )
                self._episodes.append(episode)
    
    def __repr__(self) -> str:
        return f"BBCiPlayerSeries(pid={self.pid}, title={self.title})"


class BBCiPlayerSeason:
    def __init__(self, series: BBCiPlayerSeries):
        self.series = series
        self._episodes = None
        self.url = series.url
        self.season_number = 1
    
    @property
    def title(self) -> str:
        return self.series.title
    
    @property
    def episodes(self) -> List[BBCiPlayerEpisode]:
        if self._episodes is None:
            self.series._load_episodes()
            self._episodes = self.series._episodes
        return self._episodes
    
    @property
    def episode_count(self) -> int:
        return len(self.episodes)
    
    def download(self, path: Optional[str] = None) -> bool:
        return self.series.download(path)
    
    def watch(self, player: str = "mpv", **kwargs) -> bool:
        return self.series.watch(player=player, **kwargs)
    
    def syncplay(self, **kwargs) -> bool:
        return self.series.syncplay(**kwargs)
    
    def __repr__(self) -> str:
        return f"BBCiPlayerSeason(series={self.series.title}, episodes={self.episode_count})"
