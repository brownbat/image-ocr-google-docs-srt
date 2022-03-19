import os
from pathlib import Path
import io

CREDS_FILE_LOCATION = os.path.join(os.getcwd(),"token.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDS_FILE_LOCATION

from google.cloud import vision


def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    retval = None
    if len(texts) > 0:
        retval = texts[0].description
        # retval += '\n'    
    
    return retval


def main():
    current_directory = os.getcwd()
    images_dir = Path(os.path.join(f'{current_directory}','images'))
    raw_texts_dir = Path(os.path.join(f'{current_directory}','raw_texts'))
    texts_dir = Path(os.path.join(f'{current_directory}','texts'))
    srt_file = open(os.path.join(f'{current_directory}','subtitle_output.srt'), 'w', encoding='utf-8')
    
    # check dir exists
    if not images_dir.exists():
        images_dir.mkdir()
        print('Images folder is empty.')
        exit()

    images = Path(f'{current_directory}/images').rglob('*.jpeg')
    line = 1

    for image in images:
        # Get data
        imgname = str(image.name)
        text_content = detect_text(image)

        if text_content is not None:
            text_content = text_content.strip()
            start_hour = imgname.split('_')[0][:2]
            start_min = imgname.split('_')[1][:2]
            start_sec = imgname.split('_')[2][:2]
            start_micro = imgname.split('_')[3][:3]

            end_hour = imgname.split('__')[1].split('_')[0][:2]
            end_min = imgname.split('__')[1].split('_')[1][:2]
            end_sec = imgname.split('__')[1].split('_')[2][:2]
            end_micro = imgname.split('__')[1].split('_')[3][:3]

            # Format start time
            start_time = f'{start_hour}:{start_min}:{start_sec},{start_micro}'

            # Format end time
            end_time = f'{end_hour}:{end_min}:{end_sec},{end_micro}'

            # Append the line to srt file
            srt_file.writelines([
                f'{line}\n',
                f'{start_time} --> {end_time}\n',
                f'{text_content}\n\n'
            ])
            print(f"""{line}: {start_time}\n{text_content}\n\n""")
            line += 1

    srt_file.close()


if __name__ == '__main__':
    main()
