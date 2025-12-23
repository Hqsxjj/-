from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import textwrap
import requests
import io
import os

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_font(font_path: str, size: int):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Warning: Could not load font {font_path}. Using default font.")
        return ImageFont.load_default()

def generate_emby_cover(
    library_name: str,
    sub_title: str,
    posters: list[str],
    backdrop_url: str,
    theme: dict,
    layout_mode: str,
    current_font: dict,
    active_text_color: str,
    title_x: int,
    title_y: int,
    title_gap: int,
    title_size: int,
    grid_intensity: int,
    poster_x: int,
    fan_spread: int,
    fan_rotation: int,
    cycle_index: int
):
    # Define output dimensions
    width, height = 800, 1200 # Standard poster aspect ratio 2:3

    # Create a blank image with the theme background
    if theme and theme.get('bgStyle', '').startswith('linear-gradient'):
        # For simplicity, we'll just pick a dominant color from the gradient
        # A full gradient rendering would be more complex and might require aggdraw
        bg_color_str = theme['bgStyle'].split(',')[1].strip().split(' ')[0] # E.g., #0f0c29
        try:
            bg_color = hex_to_rgb(bg_color_str)
        except ValueError:
            bg_color = (0, 0, 0) # Default to black
    else:
        bg_color = (0, 0, 0) # Default to black

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Load backdrop image if provided
    if backdrop_url:
        try:
            response = requests.get(backdrop_url)
            response.raise_for_status()
            backdrop_img = Image.open(io.BytesIO(response.content)).convert('RGB')
            backdrop_img = backdrop_img.resize((width, height), Image.LANCZOS)
            
            # Apply a subtle darkening if theme is dark
            if theme.get('isDark', False):
                enhancer = ImageEnhance.Brightness(backdrop_img)
                backdrop_img = enhancer.enhance(0.7) # Darken by 30%

            img.paste(backdrop_img, (0, 0))
        except Exception as e:
            print(f"Error loading backdrop image: {e}")

    # Placeholder for posters (implement stack mode first)
    # This will need to be much more sophisticated based on App.tsx logic
    if posters and layout_mode == 'stack':
        poster_size = (int(width * 0.7), int(height * 0.7)) # Example size
        current_y = height // 2 - poster_size[1] // 2
        for p_url in posters[:3]: # Limit to 3 for simplicity
            try:
                response = requests.get(p_url)
                response.raise_for_status()
                poster_img = Image.open(io.BytesIO(response.content)).convert('RGBA')
                poster_img = poster_img.resize(poster_size, Image.LANCZOS)
                
                # Create a blank image with alpha for pasting
                temp_img = Image.new('RGBA', img.size, (0,0,0,0))
                temp_img.paste(poster_img, (width // 2 - poster_size[0] // 2, current_y))
                img = Image.alpha_composite(img.convert('RGBA'), temp_img).convert('RGB')
                current_y += 50 # Stack them slightly offset
            except Exception as e:
                print(f"Error loading poster: {e}")

    # Text rendering
    # Adjust font paths as needed. You might need to bundle fonts or use system fonts.
    # For now, using a generic font or system default.
    font_family = current_font.get('family', "Inter") # Default font from frontend
    text_color = hex_to_rgb(active_text_color)

    # Library Name
    try:
        # Attempt to load a common system font, or fall back to default
        lib_font = get_font(f"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", title_size) 
    except:
        lib_font = get_font(f"/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", title_size) or ImageFont.load_default()

    wrapped_library_name = textwrap.wrap(library_name, width=20) # Adjust width as needed
    y_text = title_y
    for line in wrapped_library_name:
        text_width, text_height = draw.textbbox((0,0), line, font=lib_font)[2:]
        draw.text((title_x, y_text), line, font=lib_font, fill=text_color)
        y_text += text_height + title_gap

    # Subtitle
    try:
        sub_font = get_font(f"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", title_size // 2)
    except:
        sub_font = get_font(f"/usr/share/fonts/truetype/freefont/FreeSans.ttf", title_size // 2) or ImageFont.load_default()
        
    wrapped_sub_title = textwrap.wrap(sub_title, width=30)
    for line in wrapped_sub_title:
        text_width, text_height = draw.textbbox((0,0), line, font=sub_font)[2:]
        draw.text((title_x, y_text), line, font=sub_font, fill=text_color)
        y_text += text_height + (title_gap // 2)

    output_path = "generated_cover.png"
    img.save(output_path)
    return output_path