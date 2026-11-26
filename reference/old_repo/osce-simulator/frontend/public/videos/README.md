# Video Files Directory

This directory contains video files for the OSCE Simulator tutorial.

## Tutorial Video

**File Name:** `Tutorial.mov`

**Location:** Place your `Tutorial.mov` file directly in this directory.

**Supported Formats:**
- Primary: `Tutorial.mov` (QuickTime)
- Fallback: `Tutorial.mp4` (MP4)
- Web: `Tutorial.webm` (WebM)

## Video Specifications

For optimal performance, your tutorial video should:
- Be in `.mov` format (QuickTime)
- Have a resolution of 1920x1080 (Full HD) or higher
- Be compressed for web delivery (H.264 codec recommended)
- Have a reasonable file size for web streaming

## Poster Image (Optional)

You can also add a poster image:
- **File Name:** `tutorial-poster.jpg`
- **Purpose:** Thumbnail shown before video plays
- **Recommended Size:** 1920x1080 pixels

## File Structure

```
public/videos/
├── Tutorial.mov          # Your tutorial video (required)
├── Tutorial.mp4          # MP4 fallback (optional)
├── Tutorial.webm         # WebM fallback (optional)
├── tutorial-poster.jpg   # Poster image (optional)
└── README.md            # This file
```

## Access

The tutorial video will be accessible at:
- **URL:** `/tutorial`
- **Video Path:** `/videos/Tutorial.mov`

The tutorial page is designed to be a standalone showcase of the Theia OSCE Simulator platform.
