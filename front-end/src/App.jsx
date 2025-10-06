// src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:4000';

function App() {
  const [videos, setVideos] = useState([]);
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [channelsLoading, setChannelsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedChannelId, setSelectedChannelId] = useState('');
  const [expandedDescriptions, setExpandedDescriptions] = useState({});

  const fetchChannels = async () => {
    try {
      setChannelsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/subs-info`);

      if (response.data && Array.isArray(response.data)) {
        const formattedChannels = response.data.map(channel => {
          // Extract the channel ID from the _id field
          const channelId = channel._id.replace('yt:channel:', '');
          return {
            id: channelId,
            _id: channel._id,
            last_video_update: channel.last_video_update,
            new_vids: channel.new_vids,
            time_between_fetches: channel.time_between_fetches,
            videos: channel.videos
          };
        });
        setChannels(formattedChannels);
      }
    } catch (err) {
      console.error('Error fetching channels:', err);
      setError('Failed to fetch available channels.');
    } finally {
      setChannelsLoading(false);
    }
  };

  const fetchVideos = async (channelId) => {
    try {
      setLoading(true);
      setError(null);
      setExpandedDescriptions({}); // Reset expanded states when fetching new videos

      const apiUrl = `${API_BASE_URL}/vid-from-link/yt:channel:${channelId}`;
      const response = await axios.get(apiUrl);

      if (response.data && Array.isArray(response.data)) {
        setVideos(response.data);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      setError('Failed to fetch videos. Please check the channel and ensure the API is running.');
      console.error('Error fetching videos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  useEffect(() => {
    if (selectedChannelId) {
      fetchVideos(selectedChannelId);
    }
  }, [selectedChannelId]);

  const handleChannelChange = (e) => {
    setSelectedChannelId(e.target.value);
  };

  const handleRefreshChannels = () => {
    fetchChannels();
  };

  const toggleDescription = (videoId) => {
    setExpandedDescriptions(prev => ({
      ...prev,
      [videoId]: !prev[videoId]
    }));
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const formatRelativeTime = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

      if (diffInHours < 1) {
        return 'Just now';
      } else if (diffInHours < 24) {
        return `${diffInHours}h ago`;
      } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays}d ago`;
      }
    } catch {
      return dateString;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YouTube Channel Videos</h1>

        <div className="channel-selector">
          <div className="selector-header">
            <label htmlFor="channel-select">Select Channel:</label>
            <button
              onClick={handleRefreshChannels}
              className="refresh-button"
              disabled={channelsLoading}
            >
              {channelsLoading ? 'Refreshing...' : '↻ Refresh'}
            </button>
          </div>

          <select
            id="channel-select"
            value={selectedChannelId}
            onChange={handleChannelChange}
            className="channel-select"
            disabled={channelsLoading || channels.length === 0}
          >
            {channelsLoading ? (
              <option value="">Loading channels...</option>
            ) : channels.length === 0 ? (
              <option value="">No channels available</option>
            ) : (
              <>
                <option value="">Choose a channel...</option>
                {channels.map((channel) => (
                  <option key={channel.id} value={channel.id}>
                    {channel.id} ({channel.videos} videos, {channel.new_vids} new)
                  </option>
                ))}
              </>
            )}
          </select>

          {selectedChannelId && channels.length > 0 && (
            <div className="channel-info">
              <p>
                Selected: <strong>{selectedChannelId}</strong>
                {channels.find(ch => ch.id === selectedChannelId)?.last_video_update && (
                  <span> • Last updated: {formatRelativeTime(channels.find(ch => ch.id === selectedChannelId).last_video_update)}</span>
                )}
              </p>
            </div>
          )}
        </div>
      </header>

      <main className="main-content">
        {channelsLoading && <div className="loading">Loading channels...</div>}

        {error && (
          <div className="error">
            {error}
            <button onClick={() => selectedChannelId && fetchVideos(selectedChannelId)} className="retry-button">
              Try Again
            </button>
          </div>
        )}

        {!channelsLoading && channels.length === 0 && !error && (
          <div className="no-channels">
            <h3>No channels available</h3>
            <p>No YouTube channels found in the subscription list.</p>
            <button onClick={handleRefreshChannels} className="retry-button">
              Refresh Channels
            </button>
          </div>
        )}

        {loading && selectedChannelId && (
          <div className="loading">Loading videos for {selectedChannelId}...</div>
        )}

        {!loading && !error && selectedChannelId && (
          <div className="videos-container">
            <h2>
              Latest Videos from {selectedChannelId}
              {videos.length > 0 && ` (${videos.length})`}
            </h2>
            <div className="videos-grid">
              {videos.sort((a, b) => new Date(b.published) - new Date(a.published)).map((video) => (
                <div key={video.id} className="video-card">
                  <div className="video-thumbnail">
                    <img
                      src={video.thumbnail}
                      alt={video.title}
                      className="thumbnail-image"
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x180/333/fff?text=No+Thumbnail';
                      }}
                    />
                    <div className="play-button">▶</div>
                  </div>

                  <div className="video-info">
                    <h3
                      className="video-title"
                      title={video.title}
                    >
                      {video.title}
                    </h3>
                    <p className="video-author">
                      By: <a
                        href={video.author_channel}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="channel-link"
                      >
                        {video.author}
                      </a>
                    </p>
                    <p className="video-date">Published: {formatDate(video.published)}</p>
                    {video.updated && (
                      <p className="video-date">Updated: {formatDate(video.updated)}</p>
                    )}

                    {video.summary && (
                      <div className="video-summary">
                        <p className={expandedDescriptions[video.id] ? 'expanded' : 'collapsed'}>
                          {video.summary}
                        </p>
                        {video.summary.length > 100 && (
                          <button
                            className="expand-button"
                            onClick={() => toggleDescription(video.id)}
                          >
                            {expandedDescriptions[video.id] ? 'Show Less' : 'Show More'}
                          </button>
                        )}
                      </div>
                    )}

                    <div className="video-actions">
                      <a
                        href={video.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="watch-button"
                      >
                        Watch on YouTube
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!loading && !error && selectedChannelId && videos.length === 0 && (
          <div className="no-videos">
            <h3>No videos found for this channel</h3>
            <p>The channel might not have any videos or there was an issue loading them.</p>
          </div>
        )}

        {!channelsLoading && !selectedChannelId && channels.length > 0 && (
          <div className="no-selection">
            <h3>Please select a channel to view videos</h3>
            <p>Choose a channel from the dropdown above to see its latest videos.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
