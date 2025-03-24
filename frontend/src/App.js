import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Card,
  CardMedia,
  CardContent,
  Tabs,
  Tab,
  Paper,
  Grid,
  Link,
  Snackbar,
  Alert,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ButtonGroup,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import YouTubeIcon from '@mui/icons-material/YouTube';
import SummarizeIcon from '@mui/icons-material/Summarize';
import TranslateIcon from '@mui/icons-material/Translate';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import ImageIcon from '@mui/icons-material/Image';
import CloseIcon from '@mui/icons-material/Close';
import UpgradeIcon from '@mui/icons-material/Upgrade';
import HighQualityIcon from '@mui/icons-material/HighQuality';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import FourKIcon from '@mui/icons-material/FourK';
import EightKIcon from '@mui/icons-material/EightK';
import axios from 'axios';

// Use environment variable for API URL or fallback to localhost for development
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [languageTab, setLanguageTab] = useState(0);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [thumbnailDownloading, setThumbnailDownloading] = useState(false);
  const [thumbnailUrl, setThumbnailUrl] = useState('');
  const [thumbnailDialogOpen, setThumbnailDialogOpen] = useState(false);
  const [upscaledThumbnailUrl, setUpscaledThumbnailUrl] = useState('');
  const [isUpscaling, setIsUpscaling] = useState(false);
  const [showUpscaled, setShowUpscaled] = useState(false);
  const [currentResolution, setCurrentResolution] = useState('');
  const [upscaleMenuAnchor, setUpscaleMenuAnchor] = useState(null);

  const handleVideoUrlChange = (event) => {
    setVideoUrl(event.target.value);
  };

  const handleLanguageTabChange = (event, newValue) => {
    setLanguageTab(newValue);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleThumbnailDialogOpen = () => {
    setThumbnailDialogOpen(true);
  };

  const handleThumbnailDialogClose = () => {
    setThumbnailDialogOpen(false);
    // Reset to original view when closing
    setShowUpscaled(false);
  };

  const handleUpscaleMenuOpen = (event) => {
    setUpscaleMenuAnchor(event.currentTarget);
  };

  const handleUpscaleMenuClose = () => {
    setUpscaleMenuAnchor(null);
  };

  const handleSubmit = async () => {
    // Basic URL validation
    if (!videoUrl.includes('youtube.com') && !videoUrl.includes('youtu.be')) {
      setError('Please enter a valid YouTube URL');
      setSnackbarOpen(true);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setThumbnailUrl('');
    setUpscaledThumbnailUrl('');
    setShowUpscaled(false);
    setCurrentResolution('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/summarize`, {
        video_url: videoUrl
      });

      setResult(response.data);
      
      // Download the high-quality thumbnail for the video
      downloadThumbnail();
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while summarizing the video');
      setSnackbarOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const downloadThumbnail = async () => {
    if (!videoUrl) return;
    
    setThumbnailDownloading(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/api/download-thumbnail`, {
        video_url: videoUrl
      });
      
      if (response.data.success) {
        // Use the thumbnail URL
        setThumbnailUrl(`${API_BASE_URL}${response.data.url}`);
      }
    } catch (err) {
      console.error("Error downloading thumbnail:", err);
    } finally {
      setThumbnailDownloading(false);
    }
  };
  
  const upscaleThumbnail = async (scaleFactor = 2, targetResolution = null) => {
    if (!videoUrl) return;
    
    handleUpscaleMenuClose();
    setIsUpscaling(true);
    
    try {
      const requestData = {
        video_url: videoUrl,
        scale_factor: scaleFactor
      };
      
      // Add target_resolution if provided
      if (targetResolution) {
        requestData.target_resolution = targetResolution;
      }
      
      const response = await axios.post(`${API_BASE_URL}/api/upscale-thumbnail`, requestData);
      
      if (response.data.success) {
        // Use the upscaled thumbnail URL
        setUpscaledThumbnailUrl(`${API_BASE_URL}${response.data.upscaled_url}`);
        // Automatically show upscaled version when available
        setShowUpscaled(true);
        // Store current resolution for display
        setCurrentResolution(response.data.resolution || `${scaleFactor}x`);
        
        // Show success message
        setError(`Thumbnail successfully upscaled to ${targetResolution || `${scaleFactor}x`}!`);
        setSnackbarOpen(true);
      }
    } catch (err) {
      console.error("Error upscaling thumbnail:", err);
      setError('Failed to upscale thumbnail. Please try again.');
      setSnackbarOpen(true);
    } finally {
      setIsUpscaling(false);
    }
  };
  
  // Handle 2x upscale - most common case
  const handleStandardUpscale = () => {
    upscaleThumbnail(2);
  };
  
  // Handle 4K upscale
  const handle4KUpscale = () => {
    upscaleThumbnail(null, '4K');
  };
  
  // Handle 8K upscale
  const handle8KUpscale = () => {
    upscaleThumbnail(null, '8K');
  };
  
  const toggleThumbnailVersion = () => {
    setShowUpscaled(!showUpscaled);
  };
  
  const openThumbnailInNewTab = () => {
    const urlToOpen = showUpscaled && upscaledThumbnailUrl 
      ? upscaledThumbnailUrl 
      : (thumbnailUrl || result?.video_info?.thumbnail);
      
    if (urlToOpen) {
      window.open(urlToOpen, '_blank');
    }
  };

  const downloadThumbnailToComputer = () => {
    if (!result) return;
    
    // Get the filename from the video ID or title
    const resolutionSuffix = showUpscaled && currentResolution ? `-${currentResolution}` : '';
    const filename = result.video_info.id 
      ? `youtube-thumbnail-${result.video_info.id}${showUpscaled ? '-upscaled' + resolutionSuffix : ''}.jpg` 
      : `youtube-thumbnail-${Date.now()}${showUpscaled ? '-upscaled' + resolutionSuffix : ''}.jpg`;
    
    // Create a download link
    const link = document.createElement('a');
    link.href = showUpscaled && upscaledThumbnailUrl 
      ? upscaledThumbnailUrl 
      : (thumbnailUrl || result.video_info.thumbnail);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            mb: 4
          }}
        >
          <YouTubeIcon sx={{ fontSize: 40, color: 'primary.main', mr: 1 }} />
          <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            YouTube Video Summarizer
          </Typography>
        </Box>

        <Typography variant="h6" color="text.secondary" paragraph>
          Get concise summaries of YouTube videos in Hindi and English
        </Typography>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 4, 
            mt: 4, 
            mb: 6, 
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
          }}
        >
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={9}>
              <TextField
                fullWidth
                label="Enter YouTube Video URL"
                variant="outlined"
                value={videoUrl}
                onChange={handleVideoUrlChange}
                placeholder="https://www.youtube.com/watch?v=..."
                InputProps={{
                  startAdornment: (
                    <YouTubeIcon sx={{ mr: 1, color: 'primary.main' }} />
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                onClick={handleSubmit}
                disabled={loading || !videoUrl}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SummarizeIcon />}
                sx={{ height: '56px' }}
              >
                {loading ? 'Summarizing...' : 'Summarize'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {result && (
          <Box sx={{ mt: 4 }}>
            <Card sx={{ mb: 4, overflow: 'hidden' }}>
              <Box sx={{ position: 'relative' }}>
                <CardMedia
                  component="img"
                  height="300"
                  image={showUpscaled && upscaledThumbnailUrl ? upscaledThumbnailUrl : (thumbnailUrl || result.video_info.thumbnail)}
                  alt={result.video_info.title}
                  sx={{ objectFit: 'cover', cursor: 'pointer' }}
                  onClick={handleThumbnailDialogOpen}
                />
                
                {/* Thumbnail Actions */}
                <Box 
                  sx={{ 
                    position: 'absolute', 
                    bottom: 16, 
                    right: 16, 
                    display: 'flex',
                    gap: 1
                  }}
                >
                  <Tooltip title="View Full Image">
                    <IconButton 
                      color="primary" 
                      sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
                      onClick={handleThumbnailDialogOpen}
                    >
                      <ImageIcon />
                    </IconButton>
                  </Tooltip>
                  
                  {/* Upscale Button Group with Menu */}
                  <Box>
                    <ButtonGroup 
                      variant="contained" 
                      color="primary"
                      sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
                      disabled={isUpscaling || !thumbnailUrl}
                    >
                      <Tooltip title="Upscale Thumbnail">
                        <IconButton
                          color="primary"
                          onClick={handleStandardUpscale}
                          disabled={isUpscaling || !thumbnailUrl}
                        >
                          {isUpscaling ? <CircularProgress size={24} /> : <UpgradeIcon />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="More Upscale Options">
                        <IconButton
                          color="primary"
                          size="small"
                          onClick={handleUpscaleMenuOpen}
                          disabled={isUpscaling || !thumbnailUrl}
                        >
                          <ArrowDropDownIcon />
                        </IconButton>
                      </Tooltip>
                    </ButtonGroup>
                    <Menu
                      anchorEl={upscaleMenuAnchor}
                      open={Boolean(upscaleMenuAnchor)}
                      onClose={handleUpscaleMenuClose}
                    >
                      <MenuItem onClick={handleStandardUpscale} disabled={isUpscaling}>
                        <ListItemIcon>
                          <UpgradeIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText>Standard (2x)</ListItemText>
                      </MenuItem>
                      <MenuItem onClick={handle4KUpscale} disabled={isUpscaling}>
                        <ListItemIcon>
                          <FourKIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText>4K Ultra HD</ListItemText>
                      </MenuItem>
                      <MenuItem onClick={handle8KUpscale} disabled={isUpscaling}>
                        <ListItemIcon>
                          <EightKIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText>8K Super HD</ListItemText>
                      </MenuItem>
                    </Menu>
                  </Box>
                  
                  <Tooltip title="Download Thumbnail">
                    <IconButton 
                      color="primary" 
                      sx={{ backgroundColor: 'rgba(255, 255, 255, 0.9)' }}
                      onClick={downloadThumbnailToComputer}
                      disabled={thumbnailDownloading}
                    >
                      {thumbnailDownloading ? <CircularProgress size={24} /> : <FileDownloadIcon />}
                    </IconButton>
                  </Tooltip>
                </Box>
                
                {/* Resolution Badge when showing upscaled thumbnail */}
                {showUpscaled && upscaledThumbnailUrl && currentResolution && (
                  <Box 
                    sx={{ 
                      position: 'absolute', 
                      top: 16, 
                      right: 16, 
                      bgcolor: 'rgba(0, 0, 0, 0.6)',
                      color: 'white',
                      px: 1.5,
                      py: 0.5,
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 0.5
                    }}
                  >
                    <HighQualityIcon fontSize="small" />
                    <Typography variant="body2" fontWeight="bold">
                      {currentResolution.toUpperCase().includes('K') ? currentResolution : `${currentResolution} Upscaled`}
                    </Typography>
                  </Box>
                )}
              </Box>
              
              <CardContent>
                <Typography variant="h5" component="div" gutterBottom>
                  {result.video_info.title}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  {result.video_info.channel}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mr: 3 }}>
                    {Math.floor(result.video_info.duration / 60)}:{(result.video_info.duration % 60).toString().padStart(2, '0')} mins
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Intl.NumberFormat().format(result.video_info.view_count)} views
                  </Typography>
                </Box>
              </CardContent>
            </Card>

            <Paper sx={{ mb: 4, borderRadius: 3 }}>
              <Tabs 
                value={languageTab} 
                onChange={handleLanguageTabChange} 
                centered
                variant="fullWidth"
                sx={{
                  borderBottom: 1,
                  borderColor: 'divider',
                  '& .MuiTab-root': {
                    py: 2
                  }
                }}
              >
                <Tab 
                  label="English Summary" 
                  icon={<SummarizeIcon />} 
                  iconPosition="start"
                />
                <Tab 
                  label="Hindi Summary" 
                  icon={<TranslateIcon />} 
                  iconPosition="start"
                />
              </Tabs>

              <Box p={4}>
                {languageTab === 0 ? (
                  <Typography variant="body1" paragraph>
                    {result.english_summary}
                  </Typography>
                ) : (
                  <Typography variant="body1" paragraph>
                    {result.hindi_summary}
                  </Typography>
                )}
              </Box>
            </Paper>

            <Box sx={{ textAlign: 'center', mt: 6, mb: 2 }}>
              <Link href={`https://www.youtube.com/watch?v=${result.video_info.id}`} target="_blank" rel="noopener">
                <Button
                  variant="outlined"
                  color="primary"
                  startIcon={<YouTubeIcon />}
                >
                  Watch Original Video
                </Button>
              </Link>
            </Box>
          </Box>
        )}
      </Box>

      {/* Footer */}
      <Box sx={{ py: 3, textAlign: 'center', mt: 4 }}>
        <Typography variant="body2" color="text.secondary">
          YouTube Video Summarizer &copy; {new Date().getFullYear()}
        </Typography>
      </Box>

      {/* Error Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity={error.includes('successfully') ? 'success' : 'error'} sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
      
      {/* Thumbnail Dialog */}
      <Dialog
        open={thumbnailDialogOpen}
        onClose={handleThumbnailDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {showUpscaled && currentResolution ? 
            `High Quality Thumbnail (${currentResolution.toUpperCase().includes('K') ? currentResolution : `${currentResolution} Upscaled`})` : 
            'High Quality Thumbnail'}
          <IconButton
            aria-label="close"
            onClick={handleThumbnailDialogClose}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 2 }}>
            <img 
              src={showUpscaled && upscaledThumbnailUrl ? upscaledThumbnailUrl : (thumbnailUrl || (result?.video_info?.thumbnail || ''))} 
              alt="Video Thumbnail" 
              style={{ maxWidth: '100%', maxHeight: '70vh' }}
            />
            
            {upscaledThumbnailUrl && (
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="outlined" 
                  color="primary" 
                  onClick={toggleThumbnailVersion}
                  startIcon={showUpscaled ? <ImageIcon /> : <HighQualityIcon />}
                  sx={{ mt: 1 }}
                >
                  {showUpscaled ? 'Show Original' : 'Show Upscaled Version'}
                </Button>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          {/* Upscale button with dropdown menu */}
          <ButtonGroup variant="outlined" disabled={isUpscaling || !thumbnailUrl}>
            <Button 
              onClick={handleStandardUpscale}
              startIcon={isUpscaling ? <CircularProgress size={20} /> : <UpgradeIcon />}
              disabled={isUpscaling || !thumbnailUrl}
            >
              {isUpscaling ? 'Upscaling...' : 'Upscale (2x)'}
            </Button>
            <Button
              size="small"
              aria-label="select upscale resolution"
              aria-haspopup="true"
              onClick={handleUpscaleMenuOpen}
              disabled={isUpscaling || !thumbnailUrl}
            >
              <ArrowDropDownIcon />
            </Button>
          </ButtonGroup>

          <Button onClick={downloadThumbnailToComputer} startIcon={<FileDownloadIcon />}>
            Download
          </Button>
          <Button onClick={handleThumbnailDialogClose}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;
