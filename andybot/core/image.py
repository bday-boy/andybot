from typing import List, Union

from PIL import Image


def stack_images_vertically(img_files: List[Union[str, bytes]],
                            align_vertically: bool = True,
                            output: str = 'temp.png') -> bool:
    """Stacks a number of images on one another vertically. Returns whether
    the file was successfully saved or not.
    """
    images = [Image.open(fp) for fp in img_files]
    widths, heights = zip(*(i.size for i in images))

    max_width = max(widths)
    total_heights = sum(heights)
    new_img = Image.new('RGBA', (max_width, total_heights))

    y_offset = 0
    for img in images:
        img_width, img_height = img.size
        x_offset = align_vertically * (max_width - img_width) // 2
        new_img.paste(img, (x_offset, y_offset))
        y_offset += img_height

    try:
        new_img.save(output)
        return True
    except (OSError, ValueError):
        print(
            f'Warning: Could not save image {output} from image files '
            f'{", ".join(img_files)}.'
        )
        return False


def stack_images_horizontally(img_files: List[Union[str, bytes]],
                              align_horizontally: bool = True,
                              output: str = 'temp.png') -> bool:
    """Stacks a number of images on one another horizontally. Returns whether
    the file was successfully saved or not.
    """
    images = [Image.open(fp) for fp in img_files]
    widths, heights = zip(*(i.size for i in images))

    total_widths = sum(widths)
    max_height = max(heights)
    new_img = Image.new('RGBA', (total_widths, max_height))

    x_offset = 0
    for img in images:
        img_width, img_height = img.size
        y_offset = align_horizontally * (max_height - img_height) // 2
        new_img.paste(img, (x_offset, y_offset))
        x_offset += img_width

    try:
        new_img.save(output)
        return True
    except (OSError, ValueError):
        print(
            f'Warning: Could not save image {output} from image files '
            f'{", ".join(img_files)}.'
        )
        return False


if __name__ == '__main__':
    imgs = input('Gimme some comma-separated PNGs: ').split(',')
    images = [f'./attachments/pkmn/{x.strip()}.png' for x in imgs]
    stack_images_horizontally(images)
