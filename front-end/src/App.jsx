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
  const [showAddSubscription, setShowAddSubscription] = useState(false);
  const [subscriptionUrl, setSubscriptionUrl] = useState('');
  const [timeBetweenFetches, setTimeBetweenFetches] = useState(300); // Default 5 minutes
  const [addingSubscription, setAddingSubscription] = useState(false);
  const [subscriptionError, setSubscriptionError] = useState(null);
  const [subscriptionSuccess, setSubscriptionSuccess] = useState(null);
  const [editingSubscription, setEditingSubscription] = useState(null);
  const [newTimeBetweenFetches, setNewTimeBetweenFetches] = useState(300);
  const [updatingSubscription, setUpdatingSubscription] = useState(false);
  const [deletingSubscription, setDeletingSubscription] = useState(false);

  const fetchChannels = async () => {
    try {
      setChannelsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/subs-info`);

      if (response.data && Array.isArray(response.data)) {
        const formattedChannels = response.data.map(subscription => {
          // Extract the ID and type from the _id field
          const isPlaylist = subscription._id.startsWith('yt:playlist:');
          const id = subscription._id.replace('yt:channel:', '').replace('yt:playlist:', '');
          const type = isPlaylist ? 'playlist' : 'channel';

          return {
            id: id,
            _id: subscription._id,
            type: type,
            title: subscription.title,
            last_fetch: subscription.last_fetch,
            last_video_update: subscription.last_video_update,
            last_viewed: subscription.last_viewed,
            new_vids: subscription.new_vids,
            time_between_fetches: subscription.time_between_fetches,
            videos: subscription.videos
          };
        });
        setChannels(formattedChannels);
      }
    } catch (err) {
      console.error('Error fetching channels:', err);
      setError('Failed to fetch available subscriptions.');
    } finally {
      setChannelsLoading(false);
    }
  };

  const setViewed = async (subscriptionId, viewedTime) => {
    try {
      const formData = new FormData();
      formData.append('_id', subscriptionId);
      formData.append('viewed_time', viewedTime);

      await axios.post(`${API_BASE_URL}/set-viewed/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } catch (err) {
      console.error('Error setting viewed time:', err);
      // Don't show error to user as this is a background operation
    }
  };

  const updateTimeBetweenFetches = async (subscriptionId, newTime) => {
    try {
      setUpdatingSubscription(true);
      const formData = new FormData();
      formData.append('_id', subscriptionId);
      formData.append('time_between_fetches', newTime.toString());

      await axios.post(`${API_BASE_URL}/set-time-between-fetches/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Refresh the channels list to show updated data
      fetchChannels();
      setEditingSubscription(null);
      setSubscriptionSuccess('Fetch interval updated successfully!');
    } catch (err) {
      console.error('Error updating fetch interval:', err);
      setSubscriptionError('Failed to update fetch interval. Please try again.');
    } finally {
      setUpdatingSubscription(false);
    }
  };

  const deleteSubscription = async (subscriptionId) => {
    if (!window.confirm('Are you sure you want to delete this subscription? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingSubscription(true);
      await axios.delete(`${API_BASE_URL}/delete-sub/${subscriptionId}`);

      // If the deleted subscription was selected, clear the selection
      if (selectedChannelId === subscriptionId.replace('yt:channel:', '').replace('yt:playlist:', '')) {
        setSelectedChannelId('');
        setVideos([]);
      }

      // Refresh the channels list
      fetchChannels();
      setSubscriptionSuccess('Subscription deleted successfully!');
    } catch (err) {
      console.error('Error deleting subscription:', err);
      setSubscriptionError('Failed to delete subscription. Please try again.');
    } finally {
      setDeletingSubscription(false);
    }
  };

  const fetchVideos = async (channelId) => {
    try {
      setLoading(true);
      setError(null);
      setExpandedDescriptions({}); // Reset expanded states when fetching new videos

      // Find the full _id for the API call
      const subscription = channels.find(ch => ch.id === channelId);
      if (!subscription) return;

      const apiUrl = `${API_BASE_URL}/vid-from-link/${subscription._id}`;
      const response = await axios.get(apiUrl);

      if (response.data && Array.isArray(response.data)) {
        setVideos(response.data);

        const currentTime = new Date().toISOString();
        setViewed(subscription._id, currentTime);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      setError('Failed to fetch videos. Please check the subscription and ensure the API is running.');
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

  const formatDuration = (seconds) => {
    if (seconds < 0) {
      return '?:??';
    }

    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
  };

  const handleAddSubscription = async (e) => {
    e.preventDefault();

    if (!subscriptionUrl.trim()) {
      setSubscriptionError('Please enter a YouTube channel/playlist URL');
      return;
    }

    try {
      setAddingSubscription(true);
      setSubscriptionError(null);
      setSubscriptionSuccess(null);

      const formData = new FormData();
      formData.append('url', subscriptionUrl.trim());
      formData.append('time_between_fetches', timeBetweenFetches.toString());

      const response = await axios.post(`${API_BASE_URL}/add-sub/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data) {
        setSubscriptionSuccess('Subscription added successfully!');
        setSubscriptionUrl('');
        setTimeBetweenFetches(300);
        setShowAddSubscription(false);

        // Refresh the subs list to include the new subscription
        fetchChannels();
      } else {
        throw new Error(response.data.error || 'Failed to add subscription');
      }
    } catch (err) {
      console.error('Error adding subscription:', err);
      setSubscriptionError(
        err.response?.data?.error ||
        err.message ||
        'Failed to add subscription. Please check the URL and try again.'
      );
    } finally {
      setAddingSubscription(false);
    }
  };

  const resetSubscriptionForm = () => {
    setSubscriptionUrl('');
    setTimeBetweenFetches(300);
    setSubscriptionError(null);
    setSubscriptionSuccess(null);
  };

  const startEditingSubscription = (subscription) => {
    setEditingSubscription(subscription);
    setNewTimeBetweenFetches(subscription.time_between_fetches);
  };

  const cancelEditing = () => {
    setEditingSubscription(null);
    setNewTimeBetweenFetches(300);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>YouTube Subscriptions</h1>

        <div className="channel-selector">
          <div className="selector-header">
            <label htmlFor="channel-select">Select Subscription:</label>
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
              <option value="">Loading subscriptions...</option>
            ) : channels.length === 0 ? (
              <option value="">No subscriptions available</option>
            ) : (
              <>
                <option value="">Choose a subscription...</option>
                {channels.map((channel) => (
                  <option key={channel.id} value={channel.id}>
                    {channel.type === 'playlist' ? '📋' : '📺'} {channel.title} - {channel.id} ({channel.videos} videos, {channel.new_vids} new)
                  </option>
                ))}
              </>
            )}
          </select>

          {selectedChannelId && channels.length > 0 && (
            <div className="channel-info">
              <p className="subscription-main">
                <strong>{channels.find(ch => ch.id === selectedChannelId)?.title} - {selectedChannelId}</strong>
                <span className="subscription-type">
                  ({channels.find(ch => ch.id === selectedChannelId)?.type})
                </span>
              </p>
              {(channels.find(ch => ch.id === selectedChannelId)?.last_video_update || channels.find(ch => ch.id === selectedChannelId)?.last_fetch) && (
                <p className="last-dates">
                  {channels.find(ch => ch.id === selectedChannelId)?.last_video_update && (
                    <span className="last-updated">Last updated: {formatRelativeTime(channels.find(ch => ch.id === selectedChannelId).last_video_update)}</span>
                  )}
                  {channels.find(ch => ch.id === selectedChannelId)?.last_fetch && (
                    <span className="last-fetched">Last fetched: {formatRelativeTime(channels.find(ch => ch.id === selectedChannelId).last_fetch)}</span>
                  )}
                </p>
              )}
              <div className="subscription-actions">
                <button
                  onClick={() => startEditingSubscription(channels.find(ch => ch.id === selectedChannelId))}
                  className="edit-button"
                >
                  ⚙️ Edit
                </button>
                <button
                  onClick={() => deleteSubscription(channels.find(ch => ch.id === selectedChannelId)?._id)}
                  className="delete-button"
                  disabled={deletingSubscription}
                >
                  {deletingSubscription ? 'Deleting...' : '🗑️ Delete'}
                </button>
              </div>
            </div>
          )}
        </div>

        {editingSubscription && (
          <div className="edit-subscription-modal">
            <div className="edit-subscription-content">
              <h3>Edit Subscription</h3>
              <div className="form-group">
                <label htmlFor="edit-time-between-fetches">
                  Fetch Interval (seconds):
                </label>
                <input
                  id="edit-time-between-fetches"
                  type="number"
                  value={newTimeBetweenFetches}
                  onChange={(e) => setNewTimeBetweenFetches(parseInt(e.target.value) || 0)}
                  min="60"
                  max="86400"
                  className="subscription-input"
                  disabled={updatingSubscription}
                />
                <small className="interval-help">
                  How often to check for new videos (current: {editingSubscription.time_between_fetches}s)
                </small>
              </div>
              <div className="form-actions">
                <button
                  onClick={() => updateTimeBetweenFetches(editingSubscription._id, newTimeBetweenFetches)}
                  className="submit-subscription"
                  disabled={updatingSubscription}
                >
                  {updatingSubscription ? 'Updating...' : 'Update'}
                </button>
                <button
                  onClick={cancelEditing}
                  className="cancel-button"
                  disabled={updatingSubscription}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="subscription-section">
          <button
            onClick={() => {
              setShowAddSubscription(!showAddSubscription);
              resetSubscriptionForm();
            }}
            className="add-subscription-toggle"
          >
            {showAddSubscription ? '✕ Cancel' : '+ Add Subscription'}
          </button>

          {showAddSubscription && (
            <div className="subscription-form-container">
              <form onSubmit={handleAddSubscription} className="subscription-form">
                <h3>Add New Subscription</h3>

                <div className="form-group">
                  <label htmlFor="subscription-url">YouTube Channel or Playlist URL:</label>
                  <input
                    id="subscription-url"
                    type="url"
                    value={subscriptionUrl}
                    onChange={(e) => setSubscriptionUrl(e.target.value)}
                    placeholder="https://www.youtube.com/channel/UCxxx... or https://www.youtube.com/playlist?list=PLxxx..."
                    className="subscription-input"
                    disabled={addingSubscription}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="time-between-fetches">
                    Fetch Interval (seconds):
                  </label>
                  <input
                    id="time-between-fetches"
                    type="number"
                    value={timeBetweenFetches}
                    onChange={(e) => setTimeBetweenFetches(parseInt(e.target.value) || 0)}
                    min="60"
                    max="86400"
                    className="subscription-input"
                    disabled={addingSubscription}
                  />
                  <small className="interval-help">
                    How often to check for new videos (default: 300s = 5 minutes)
                  </small>
                </div>

                {subscriptionError && (
                  <div className="subscription-error">{subscriptionError}</div>
                )}

                {subscriptionSuccess && (
                  <div className="subscription-success">{subscriptionSuccess}</div>
                )}

                <div className="form-actions">
                  <button
                    type="submit"
                    className="submit-subscription"
                    disabled={addingSubscription || !subscriptionUrl.trim()}
                  >
                    {addingSubscription ? 'Adding...' : 'Add Subscription'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      </header>

      <main className="main-content">
        {channelsLoading && <div className="loading">Loading subscriptions...</div>}

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
            <h3>No subscriptions available</h3>
            <p>No YouTube channels or playlists found in the subscription list.</p>
            <button onClick={handleRefreshChannels} className="retry-button">
              Refresh Subscriptions
            </button>
          </div>
        )}

        {loading && selectedChannelId && (
          <div className="loading">Loading videos for {channels.find(ch => ch.id === selectedChannelId)?.title}...</div>
        )}

        {!loading && !error && selectedChannelId && (
          <div className="videos-container">
            <h2>
              Latest Videos from {channels.find(ch => ch.id === selectedChannelId)?.title}
              <span className="subscription-id"> - {selectedChannelId}</span>
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
                    <div className="duration-overlay">
                      {formatDuration(video.duration)}
                    </div>
                    {channels.find(ch => ch.id === selectedChannelId)?.last_viewed &&
                     new Date(video.published) > new Date(channels.find(ch => ch.id === selectedChannelId).last_viewed) && (
                      <div className="new-overlay">NEW</div>
                    )}
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
            <h3>No videos found for this subscription</h3>
            <p>The channel or playlist might not have any videos or there was an issue loading them.</p>
          </div>
        )}

        {!channelsLoading && !selectedChannelId && channels.length > 0 && (
          <div className="no-selection">
            <h3>Please select a subscription to view videos</h3>
            <p>Choose a channel or playlist from the dropdown above to see its latest videos.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
