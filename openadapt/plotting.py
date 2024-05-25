"""Plotting utilities."""

import math

import matplotlib.pyplot as plt
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from openadapt.config import PERFORMANCE_PLOTS_DIR_PATH, config
from openadapt.models import ActionEvent


# TODO: move parameters to config
def draw_ellipse(
    x: float,
    y: float,
    image: Image.Image,
    width_pct: float = 0.03,
    height_pct: float = 0.03,
    fill_transparency: float = 0.25,
    outline_transparency: float = 0.5,
    outline_width: int = 2,
) -> tuple[Image.Image, float, float]:
    """Draw an ellipse on the image.

    Args:
        x (float): The x-coordinate of the center of the ellipse.
        y (float): The y-coordinate of the center of the ellipse.
        image (Image.Image): The image to draw on.
        width_pct (float): The percentage of the image width
          for the width of the ellipse.
        height_pct (float): The percentage of the image height
          for the height of the ellipse.
        fill_transparency (float): The transparency of the ellipse fill.
        outline_transparency (float): The transparency of the ellipse outline.
        outline_width (int): The width of the ellipse outline.

    Returns:
        Image.Image: The image with the ellipse drawn on it.
        float: The width of the ellipse.
        float: The height of the ellipse.
    """
    overlay = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(overlay)
    max_dim = max(image.size)
    width = width_pct * max_dim
    height = height_pct * max_dim
    x0 = x - width / 2
    x1 = x + width / 2
    y0 = y - height / 2
    y1 = y + height / 2
    xy = (x0, y0, x1, y1)
    fill_opacity = int(255 * fill_transparency)
    outline_opacity = int(255 * outline_transparency)
    fill = (255, 0, 0, fill_opacity)
    outline = (0, 0, 0, outline_opacity)
    draw.ellipse(xy, fill=fill, outline=outline, width=outline_width)
    image = Image.alpha_composite(image, overlay)
    return image, width, height


def get_font(original_font_name: str, font_size: int) -> ImageFont.FreeTypeFont:
    """Get a font object.

    Args:
        original_font_name (str): The original font name.
        font_size (int): The font size.

    Returns:
        PIL.ImageFont.FreeTypeFont: The font object.
    """
    font_names = [
        original_font_name,
        original_font_name.lower(),
    ]
    for font_name in font_names:
        logger.debug(f"Attempting to load {font_name=}...")
        try:
            return ImageFont.truetype(font_name, font_size)
        except OSError as exc:
            logger.debug(f"Unable to load {font_name=}, {exc=}")
    raise


def draw_text(
    x: float,
    y: float,
    text: str,
    image: Image.Image,
    font_size_pct: float = 0.01,
    font_name: str = "Arial.ttf",
    fill: tuple = (255, 0, 0),
    stroke_fill: tuple = (255, 255, 255),
    stroke_width: int = 3,
    outline: bool = False,
    outline_padding: int = 10,
) -> Image.Image:
    """Draw text on the image.

    Args:
        x (float): The x-coordinate of the text anchor point.
        y (float): The y-coordinate of the text anchor point.
        text (str): The text to draw.
        image (PIL.Image.Image): The image to draw on.
        font_size_pct (float): The percentage of the image size
          for the font size. Defaults to 0.01.
        font_name (str): The name of the font. Defaults to "Arial.ttf".
        fill (tuple): The color of the text. Defaults to (255, 0, 0) (red).
        stroke_fill (tuple): The color of the text stroke.
          Defaults to (255, 255, 255) (white).
        stroke_width (int): The width of the text stroke. Defaults to 3.
        outline (bool): Flag indicating whether to draw an outline
          around the text. Defaults to False.
        outline_padding (int): The padding size for the outline. Defaults to 10.

    Returns:
        PIL.Image.Image: The image with the text drawn on it.
    """
    overlay = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(overlay)
    max_dim = max(image.size)
    font_size = int(font_size_pct * max_dim)
    font = get_font(font_name, font_size)
    fill = (255, 0, 0)
    stroke_fill = (255, 255, 255)
    stroke_width = 3
    text_bbox = font.getbbox(text)
    bbox_left, bbox_top, bbox_right, bbox_bottom = text_bbox
    bbox_width = bbox_right - bbox_left
    bbox_height = bbox_bottom - bbox_top
    if outline:
        x0 = x - bbox_width / 2 - outline_padding
        x1 = x + bbox_width / 2 + outline_padding
        y0 = y - bbox_height / 2 - outline_padding
        y1 = y + bbox_height / 2 + outline_padding
        image = draw_rectangle(x0, y0, x1, y1, image, invert=True)
    xy = (x, y)
    draw.text(
        xy,
        text=text,
        font=font,
        fill=fill,
        stroke_fill=stroke_fill,
        stroke_width=stroke_width,
        # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors
        anchor="mm",
    )
    image = Image.alpha_composite(image, overlay)
    return image


def draw_rectangle(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    image: Image.Image,
    bg_color: tuple = (0, 0, 0),
    fg_color: tuple = (255, 255, 255),
    outline_color: tuple = (255, 0, 0),
    bg_transparency: float = 0.25,
    fg_transparency: float = 0,
    outline_transparency: float = 0.5,
    outline_width: int = 2,
    invert: bool = False,
) -> Image.Image:
    """Draw a rectangle on the image.

    Args:
        x0 (float): The x-coordinate of the top-left corner of the rectangle.
        y0 (float): The y-coordinate of the top-left corner of the rectangle.
        x1 (float): The x-coordinate of the bottom-right corner of the rectangle.
        y1 (float): The y-coordinate of the bottom-right corner of the rectangle.
        image (PIL.Image.Image): The image to draw on.
        bg_color (tuple): The background color of the rectangle.
          Defaults to (0, 0, 0) (black).
        fg_color (tuple): The foreground color of the rectangle.
          Defaults to (255, 255, 255) (white).
        outline_color (tuple): The color of the rectangle outline.
          Defaults to (255, 0, 0) (red).
        bg_transparency (float): The transparency of the rectangle
          background. Defaults to 0.25.
        fg_transparency (float): The transparency of the rectangle
          foreground. Defaults to 0.
        outline_transparency (float): The transparency of the rectangle
          outline. Defaults to 0.5.
        outline_width (int): The width of the rectangle outline.
          Defaults to 2.
        invert (bool): Flag indicating whether to invert the colors.
          Defaults to False.

    Returns:
        PIL.Image.Image: The image with the rectangle drawn on it.
    """
    if invert:
        bg_color, fg_color = fg_color, bg_color
        bg_transparency, fg_transparency = (
            fg_transparency,
            bg_transparency,
        )
    bg_opacity = int(255 * bg_transparency)
    overlay = Image.new("RGBA", image.size, bg_color + (bg_opacity,))
    draw = ImageDraw.Draw(overlay)
    xy = (x0, y0, x1, y1)
    fg_opacity = int(255 * fg_transparency)
    outline_opacity = int(255 * outline_transparency)
    fill = fg_color + (fg_opacity,)
    outline = outline_color + (outline_opacity,)
    draw.rectangle(xy, fill=fill, outline=outline, width=outline_width)
    image = Image.alpha_composite(image, overlay)
    return image


def display_event(
    action_event: ActionEvent,
    marker_width_pct: float = 0.03,
    marker_height_pct: float = 0.03,
    marker_fill_transparency: float = 0.25,
    marker_outline_transparency: float = 0.5,
    diff: bool = False,
) -> Image.Image:
    """Display an action event on the image.

    Args:
        action_event (ActionEvent): The action event to display.
        marker_width_pct (float): The percentage of the image width
          for the marker width. Defaults to 0.03.
        marker_height_pct (float): The percentage of the image height
          for the marker height. Defaults to 0.03.
        marker_fill_transparency (float): The transparency of the
          marker fill. Defaults to 0.25.
        marker_outline_transparency (float): The transparency of the
          marker outline. Defaults to 0.5.
        diff (bool): Flag indicating whether to display the diff image.
          Defaults to False.

    Returns:
        PIL.Image.Image: The image with the action event displayed on it.
    """
    recording = action_event.recording
    window_event = action_event.window_event
    screenshot = action_event.screenshot
    if diff and screenshot.diff:
        image = screenshot.diff.convert("RGBA")
    else:
        image = screenshot.image.convert("RGBA")
    width_ratio, height_ratio = get_scale_ratios(action_event)

    # dim area outside window event
    x0 = window_event.left * width_ratio
    y0 = window_event.top * height_ratio
    x1 = x0 + window_event.width * width_ratio
    y1 = y0 + window_event.height * height_ratio
    image = draw_rectangle(x0, y0, x1, y1, image, outline_width=5)

    # display diff bbox
    if diff:
        diff_bbox = screenshot.diff.getbbox()
        if diff_bbox:
            x0, y0, x1, y1 = diff_bbox
            image = draw_rectangle(
                x0,
                y0,
                x1,
                y1,
                image,
                outline_color=(255, 0, 0),
                bg_transparency=0,
                fg_transparency=0,
                # outline_transparency=.75,
                outline_width=20,
            )

    # draw click marker
    if action_event.name in common.MOUSE_EVENTS:
        x = action_event.mouse_x * width_ratio
        y = action_event.mouse_y * height_ratio
        image, ellipse_width, ellipse_height = draw_ellipse(x, y, image)

        # draw text
        dx = action_event.mouse_dx or 0
        dy = action_event.mouse_dy or 0
        d_text = f" {dx=} {dy=}" if dx or dy else ""
        text = f"{action_event.name}{d_text}"
        image = draw_text(x, y + ellipse_height / 2, text, image)
    elif action_event.name in common.KEY_EVENTS:
        x = recording.monitor_width * width_ratio / 2
        y = recording.monitor_height * height_ratio / 2
        text = action_event.text

        if config.SCRUB_ENABLED:
            import spacy

            if spacy.util.is_package(
                config.SPACY_MODEL_NAME
            ):  # Check if the model is installed
                from openadapt.privacy.providers.presidio import (
                    PresidioScrubbingProvider,
                )

                text = PresidioScrubbingProvider().scrub_text(text, is_separated=True)
            else:
                logger.warning(
                    f"SpaCy model not installed! {config.SPACY_MODEL_NAME=}. Using"
                    " original text."
                )

        image = draw_text(x, y, text, image, outline=True)
    else:
        raise Exception("unhandled {action_event.name=}")

    return image


def plot_performance(
    recording_timestamp: float = None,
    view_file: bool = False,
    save_file: bool = True,
    dark_mode: bool = False,
) -> str:
    """Plot the performance of the event processing and writing.

    Args:
        recording_timestamp: The timestamp of the recording (defaults to latest)
        view_file: Whether to view the file after saving it.
        save_file: Whether to save the file.
        dark_mode: Whether to use dark mode.

    Returns:
        str: a base64-encoded image of the plot, if not viewing the file
    """
    type_to_proc_times = defaultdict(list)
    type_to_timestamps = defaultdict(list)
    event_types = set()

    if dark_mode:
        plt.style.use("dark_background")

    # avoid circular import
    from openadapt.db import crud

    if not recording_timestamp:
        recording_timestamp = crud.get_latest_recording().timestamp
    perf_stats = crud.get_perf_stats(recording_timestamp)
    for perf_stat in perf_stats:
        event_type = perf_stat.event_type
        start_time = perf_stat.start_time
        end_time = perf_stat.end_time
        type_to_proc_times[event_type].append(end_time - start_time)
        event_types.add(event_type)
        type_to_timestamps[event_type].append(start_time)

    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    for event_type in type_to_proc_times:
        x = type_to_timestamps[event_type]
        y = type_to_proc_times[event_type]
        ax.scatter(x, y, label=event_type)
    ax.legend()
    ax.set_ylabel("Duration (seconds)")

    mem_stats = crud.get_memory_stats(recording_timestamp)
    timestamps = []
    mem_usages = []
    for mem_stat in mem_stats:
        mem_usages.append(mem_stat.memory_usage_bytes)
        timestamps.append(mem_stat.timestamp)

    memory_ax = ax.twinx()
    memory_ax.plot(
        timestamps,
        mem_usages,
        label="memory usage",
        color="red",
    )
    memory_ax.set_ylabel("Memory Usage (bytes)")

    if len(mem_usages) > 0:
        # Get the handles and labels from both axes
        handles1, labels1 = ax.get_legend_handles_labels()
        handles2, labels2 = memory_ax.get_legend_handles_labels()

        # Combine the handles and labels from both axes
        all_handles = handles1 + handles2
        all_labels = labels1 + labels2

        ax.legend(all_handles, all_labels)

    ax.set_title(f"{recording_timestamp=}")

    # TODO: add PROC_WRITE_BY_EVENT_TYPE
    if save_file:
        fname_parts = ["performance", str(recording_timestamp)]
        fname = "-".join(fname_parts) + ".png"
        os.makedirs(PERFORMANCE_PLOTS_DIR_PATH, exist_ok=True)
        fpath = os.path.join(PERFORMANCE_PLOTS_DIR_PATH, fname)
        logger.info(f"{fpath=}")
        plt.savefig(fpath)
        if view_file:
            if sys.platform == "darwin":
                os.system(f"open {fpath}")
            else:
                os.system(f"start {fpath}")
    else:
        plt.savefig(BytesIO(), format="png")  # save fig to void
        if view_file:
            plt.show()
        else:
            plt.close()
        return image2utf8(
            Image.frombytes(
                "RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb()
            )
        )


def display_binary_images_grid(
    images: list[np.ndarray],
    grid_size: tuple[int, int] | None = None,
    margin: int = 10,
) -> None:
    """Display binary arrays as images on a grid with separation between grid cells.

    Args:
        images: A list of binary numpy.ndarrays.
        grid_size: Optional tuple (rows, cols) indicating the grid size.
            If not provided, a square grid size will be calculated.
        margin: The margin size between images in the grid.
    """
    if grid_size is None:
        grid_size = (int(np.ceil(np.sqrt(len(images)))),) * 2

    # Determine max dimensions of images in the list
    max_width = max(image.shape[1] for image in images) + margin
    max_height = max(image.shape[0] for image in images) + margin

    # Create a new image with a white background
    total_width = max_width * grid_size[1] + margin
    total_height = max_height * grid_size[0] + margin
    grid_image = Image.new("1", (total_width, total_height), 1)

    for index, binary_image in enumerate(images):
        # Convert ndarray to PIL Image
        img = Image.fromarray(binary_image.astype(np.uint8) * 255, "L").convert("1")
        img_with_margin = Image.new("1", (img.width + margin, img.height + margin), 1)
        img_with_margin.paste(img, (margin // 2, margin // 2))

        # Calculate the position on the grid
        row, col = divmod(index, grid_size[1])
        x = col * max_width + margin // 2
        y = row * max_height + margin // 2

        # Paste the image into the grid
        grid_image.paste(img_with_margin, (x, y))

    # Display the grid image
    grid_image.show()


def display_images_table_with_titles(
    images: list[Image.Image],
    titles: list[str] | None = None,
    margin: int = 10,
    fontsize: int = 20,
) -> None:
    """Display RGB PIL.Images in a table layout with titles to the right of each image.

    Args:
        images: A list of RGB PIL.Images.
        titles: An optional list of strings containing titles for each image.
        margin: The margin size in pixels between images and their titles.
        fontsize: The size of the title font.
    """
    if titles is None:
        titles = [""] * len(images)
    elif len(titles) != len(images):
        raise ValueError("The length of titles must match the length of images.")

    font = get_font("Arial.ttf", fontsize)

    # Calculate the width and height required for the composite image
    max_image_width = max(image.width for image in images)
    total_height = sum(image.height for image in images) + margin * (len(images) - 1)
    max_title_height = fontsize + margin  # simple approach to calculating title height
    max_title_width = max(font.getsize(title)[0] for title in titles) + margin

    composite_image_width = max_image_width + max_title_width + margin * 3
    composite_image_height = max(
        total_height, max_title_height * len(images) + margin * (len(images) - 1)
    )

    # Create a new image to composite everything onto
    composite_image = Image.new(
        "RGB", (composite_image_width, composite_image_height), "white"
    )
    draw = ImageDraw.Draw(composite_image)

    current_y = 0
    for image, title in zip(images, titles):
        # Paste the image
        composite_image.paste(image, (margin, current_y))
        # Draw the title
        draw.text(
            (
                max_image_width + 2 * margin,
                current_y + image.height // 2 - fontsize // 2,
            ),
            title,
            fill="black",
            font=font,
        )
        current_y += image.height + margin

    composite_image.show()


def create_striped_background(
    width: int,
    height: int,
    stripe_width: int = 10,
    colors: tuple = ("blue", "red"),
) -> Image.Image:
    """
    Create an image with diagonal stripes.

    Args:
        width (int): Width of the background image.
        height (int): Height of the background image.
        stripe_width (int): Width of each stripe.
        colors (tuple): Tuple containing two colors for the stripes.

    Returns:
        Image.Image: An image with diagonal stripes.
    """
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)
    stripe_color = 0
    for i in range(-height, width + height, stripe_width):
        draw.polygon(
            [
                (i, 0),
                (i + stripe_width, 0),
                (i + height + stripe_width, height),
                (i + height, height)
            ],
            fill=colors[stripe_color],
        )
        stripe_color = 1 - stripe_color  # Switch between 0 and 1 to alternate colors
    return image


def plot_similar_image_groups(
    masked_images: list[Image.Image],
    groups: list[list[int]],
    ssim_values: list[list[float]],
    title_params: list[str] = [],
    border_size: int = 5,
    margin: int = 10,
) -> None:
    """
    Create and display a composite image for each group of similar images in a grid
    layout, with diagonal stripe pattern as background and a border around each image.

    Args:
        masked_images (list[Image.Image]): list of images to be grouped.
        groups (list[list[int]]): list of lists, where each sublist contains indices
                                  of similar images.
        ssim_values (list[list[float]]): SSIM matrix with the values between images.
        border_size (int): Size of the border around each image.
        margin (int): Margin size in pixels between images in the composite.
    """
    for group in groups:
        images_to_combine = [masked_images[idx] for idx in group]

        # Determine the grid size
        n = len(images_to_combine)
        grid_size = math.ceil(math.sqrt(n))
        max_width = max(img.width for img in images_to_combine)
        max_height = max(img.height for img in images_to_combine)

        min_group_ssim = min(ssim_values[i][j] for i in group for j in group if i != j)
        max_group_ssim = max(ssim_values[i][j] for i in group for j in group if i != j)
        title_lines = [
            f"{len(group)=}",
            f"{min_group_ssim=:.4f}",
            f"{max_group_ssim=:.4f}",
        ] + title_params

        # Calculate the dimensions of the composite image
        composite_width = grid_size * max_width + (grid_size - 1) * margin
        # Extra space for title
        composite_height = (
            grid_size * max_height + (grid_size - 1) * margin + len(title_lines) * 10
        )

        # Create striped background
        background = create_striped_background(composite_width, composite_height)

        composite_image = Image.new(
            "RGBA", (composite_width, composite_height), (0, 0, 0, 0)
        )
        composite_image.paste(background, (0, 0))

        draw = ImageDraw.Draw(composite_image)
        font = ImageFont.load_default()

        for i, title_line in enumerate(title_lines):
            draw.text((0, 10*i), title_line, font=font, fill='white')

        # Place images in a grid
        x, y = 0, len(title_lines) * 10  # Start below title space
        for idx, img in enumerate(images_to_combine):
            composite_image.paste(img, (x, y), mask=img)
            x += max_width + margin
            if (idx + 1) % grid_size == 0:
                x = 0
                y += max_height + margin

        # Display the composite image
        composite_image.show()