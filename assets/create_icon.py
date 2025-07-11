#!/usr/bin/env python3
"""
Create a simple icon for SnapSqueeze menu bar app.
This creates a basic icon that can be used for development.
"""

from PIL import Image, ImageDraw
import os

def create_icon():
    """Create a simple icon for the menu bar app."""
    # Create a 22x22 image (standard menu bar icon size)
    size = 22
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple camera/capture icon
    # Outer rectangle (camera body)
    draw.rectangle([2, 6, 20, 18], outline=(0, 0, 0, 255), width=2)
    
    # Camera lens (circle)
    draw.ellipse([7, 9, 15, 17], outline=(0, 0, 0, 255), width=2)
    
    # Lens center
    draw.ellipse([10, 12, 12, 14], fill=(0, 0, 0, 255))
    
    # Camera top (viewfinder)
    draw.rectangle([8, 4, 14, 6], outline=(0, 0, 0, 255), width=1)
    
    # Compression indicator (small arrows)
    # Left arrow pointing right
    draw.polygon([(4, 8), (6, 9), (4, 10)], fill=(0, 0, 0, 255))
    # Right arrow pointing left
    draw.polygon([(18, 8), (16, 9), (18, 10)], fill=(0, 0, 0, 255))
    
    return img

def create_template_icon():
    """Create a template icon (black with transparency) for menu bar."""
    # Template icons should be black with transparency
    size = 22
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Use solid black for template
    color = (0, 0, 0, 255)
    
    # Draw the same icon but filled
    # Camera body
    draw.rectangle([3, 7, 19, 17], fill=color)
    
    # Cut out lens area (make it transparent)
    draw.ellipse([8, 10, 14, 16], fill=(0, 0, 0, 0))
    
    # Lens ring
    draw.ellipse([8, 10, 14, 16], outline=color, width=1)
    
    # Lens center
    draw.ellipse([10, 12, 12, 14], fill=color)
    
    # Viewfinder
    draw.rectangle([9, 5, 13, 7], fill=color)
    
    # Compression arrows
    draw.polygon([(5, 9), (7, 10), (5, 11)], fill=color)
    draw.polygon([(17, 9), (15, 10), (17, 11)], fill=color)
    
    return img

def main():
    """Create the icons."""
    try:
        # Create regular icon
        icon = create_icon()
        icon.save('assets/icon.png')
        print("Created assets/icon.png")
        
        # Create template icon for menu bar
        template_icon = create_template_icon()
        template_icon.save('assets/icon_template.png')
        print("Created assets/icon_template.png")
        
        # Create different sizes for app bundle
        sizes = [16, 32, 64, 128, 256, 512]
        for size in sizes:
            resized = template_icon.resize((size, size), Image.LANCZOS)
            resized.save(f'assets/icon_{size}x{size}.png')
            print(f"Created assets/icon_{size}x{size}.png")
        
        print("Icon creation completed!")
        
    except Exception as e:
        print(f"Error creating icons: {e}")

if __name__ == "__main__":
    main()