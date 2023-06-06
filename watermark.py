from PIL import Image, ImageDraw, ImageFont

class Watermark:
    def __init__(self):
        self.watermark_image_path = "watermark/watermark.png"
        self.watermark_text = "#RushClaremont"
        # self.accepted_image = accepted_image_path

    def apply_watermark(self, accepted_image_path):
        # Open the accepted image
        accepted_image = Image.open(accepted_image_path)

        # Resize the watermark image to a desired size
        watermark_image = Image.open(self.watermark_image_path)
        watermark_width = int(accepted_image.width / 4)  # Adjust the width of the watermark image as desired
        watermark_height = int(watermark_image.height * (watermark_width / watermark_image.width))
        watermark_image = watermark_image.resize((watermark_width, watermark_height))

        # Add the watermark image to the bottom right corner of the image
        watermark_position = (accepted_image.width - watermark_image.width, accepted_image.height - watermark_image.height)
        accepted_image.paste(watermark_image, watermark_position, mask=watermark_image)

        # Calculate the position for the watermark text
        watermark_font = ImageFont.load_default()  # Adjust the font and size as desired
        text_width, text_height = watermark_font.getsize(self.watermark_text)
        text_position_x = accepted_image.width - watermark_image.width - text_width - 10
        text_position_y = accepted_image.height - text_height - 10

        # Add the watermark text to the bottom left corner of the image
        draw = ImageDraw.Draw(accepted_image)  # Create a draw object

        # Load the default font provided by PIL
        watermark_font = ImageFont.load_default()  # Adjust the font and size as desired

        # Add the watermark text to the image
        draw.text((text_position_x, text_position_y), self.watermark_text, fill=(255, 255, 255), font=watermark_font)

        # Save the watermarked image
        accepted_image.save(accepted_image_path)
