"""
Gemini AI integration for image generation and processing
"""

import json
import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
import io

logger = logging.getLogger(__name__)

class GeminiAI:
    """Gemini AI client for image generation and processing"""
    
    def __init__(self):
        self.client = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.setup_client()
    
    def setup_client(self):
        """Setup Gemini client with API key"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            logger.info("Gemini AI client initialized")
        else:
            logger.warning("GEMINI_API_KEY not found")
    
    async def generate_image(self, prompt: str, style: str = "anime") -> Optional[str]:
        """Generate image using Gemini AI"""
        if not self.client:
            return None
        
        try:
            # Enhance prompt based on style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            def _generate():
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash-preview-image-generation",
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )
                return response
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(self.executor, _generate)
            
            if response.candidates and response.candidates[0].content:
                content = response.candidates[0].content
                
                for part in content.parts:
                    if part.inline_data and part.inline_data.data:
                        # Save image to file
                        image_path = f"generated_images/image_{hash(prompt)}.png"
                        os.makedirs("generated_images", exist_ok=True)
                        
                        with open(image_path, 'wb') as f:
                            f.write(part.inline_data.data)
                        
                        return image_path
            
            return None
        
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
    
    async def analyze_image(self, image_path: str) -> Optional[str]:
        """Analyze image content using Gemini AI"""
        if not self.client:
            return None
        
        try:
            def _analyze():
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                    response = self.client.models.generate_content(
                        model="gemini-2.5-pro",
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type="image/jpeg",
                            ),
                            "Analyze this image in detail and describe its key elements, context, and any notable aspects.",
                        ],
                    )
                return response.text if response.text else ""
            
            loop = asyncio.get_event_loop()
            analysis = await loop.run_in_executor(self.executor, _analyze)
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return None
    
    async def image_to_sticker(self, image_path: str, size: tuple = (512, 512)) -> Optional[str]:
        """Convert image to sticker format"""
        try:
            def _convert():
                # Open and process image
                with Image.open(image_path) as img:
                    # Convert to RGBA if not already
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    
                    # Resize maintaining aspect ratio
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Create new image with transparent background
                    new_img = Image.new('RGBA', size, (0, 0, 0, 0))
                    
                    # Center the image
                    x = (size[0] - img.width) // 2
                    y = (size[1] - img.height) // 2
                    new_img.paste(img, (x, y), img if img.mode == 'RGBA' else None)
                    
                    # Save as PNG
                    sticker_path = f"stickers/sticker_{hash(image_path)}.png"
                    os.makedirs("stickers", exist_ok=True)
                    new_img.save(sticker_path, format='PNG')
                    
                    return sticker_path
            
            loop = asyncio.get_event_loop()
            sticker_path = await loop.run_in_executor(self.executor, _convert)
            return sticker_path
        
        except Exception as e:
            logger.error(f"Error converting to sticker: {str(e)}")
            return None
    
    async def create_text_sticker(self, text: str, style: str = "anime") -> Optional[str]:
        """Create a text-based sticker with anime styling"""
        try:
            def _create_text_sticker():
                # Create image
                size = (512, 512)
                img = Image.new('RGBA', size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Try to use a nice font, fall back to default
                try:
                    font_size = 40
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text size and position
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size[0] - text_width) // 2
                y = (size[1] - text_height) // 2
                
                # Draw outline for better visibility
                outline_width = 2
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0, 255))
                
                # Draw main text
                if style == "anime":
                    color = (255, 105, 180, 255)  # Hot pink
                else:
                    color = (255, 255, 255, 255)  # White
                
                draw.text((x, y), text, font=font, fill=color)
                
                # Save sticker
                sticker_path = f"stickers/text_sticker_{hash(text)}.png"
                os.makedirs("stickers", exist_ok=True)
                img.save(sticker_path, format='PNG')
                
                return sticker_path
            
            loop = asyncio.get_event_loop()
            sticker_path = await loop.run_in_executor(self.executor, _create_text_sticker)
            return sticker_path
        
        except Exception as e:
            logger.error(f"Error creating text sticker: {str(e)}")
            return None
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt based on style"""
        style_prompts = {
            "anime": "anime style, vibrant colors, detailed, high quality, beautiful anime art, kawaii",
            "realistic": "photorealistic, high detail, professional photography, 4K quality",
            "cartoon": "cartoon style, colorful, fun, animated, digital art",
            "cyberpunk": "cyberpunk style, neon lights, futuristic, dark atmosphere, sci-fi",
            "fantasy": "fantasy art, magical, ethereal, detailed fantasy illustration"
        }
        
        style_enhancement = style_prompts.get(style, style_prompts["anime"])
        return f"{prompt}, {style_enhancement}"
    
    def cleanup_file(self, filepath: str):
        """Clean up generated files"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Cleaned up file: {filepath}")
        except Exception as e:
            logger.error(f"Error cleaning up file: {str(e)}")

# Global AI instance
gemini_ai = GeminiAI()