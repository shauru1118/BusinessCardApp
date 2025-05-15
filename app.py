from flask import *
from html2image import Html2Image
from unidecode import unidecode

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os, time

def render_html_to_image(html_path, output_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)

    file_url = 'file://' + os.path.abspath(html_path)
    driver.get(file_url)
    time.sleep(1)

    # Снимаем полный скрин
    driver.save_screenshot("temp_full.png")

    # Находим блок визитки
    element = driver.find_element("css selector", "div.card")
    location = element.location
    size = element.size

    driver.quit()

    # Обрезаем
    x, y = int(location['x']), int(location['y'])
    w, h = int(size['width']), int(size['height'])

    from PIL import Image
    img = Image.open("temp_full.png")
    cropped = img.crop((x, y, x + w, y + h))
    cropped.save(output_path)


def del_btn(s: str) -> str:
    lines = s.split('\n')
    for line in lines:
        if line == '<div class="btn">':
            del lines[lines.index(line):lines.index(line)+5]
    
    return '\n'.join(lines)


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        job = request.form['job']
        photo = request.files['photo']
        photo.filename = unidecode(photo.filename)
        
        if len(name.split(" ")) > 2:
            ws_name = name.split(" ")
            new_name = f'<h2>{ws_name[0]}</h2> <h2>{" ".join(ws_name[1:])}</h2>'
        else:
            new_name = f"<h2>{name}</h2>"

        if photo and photo.filename.split('.')[-1] in ['jpg', 'jpeg', 'png']:
            photo_path = os.path.join('static/photoes', photo.filename)
            photo.save(photo_path)

        abs_photo_path = os.path.abspath(photo_path)
        photo_url_file = f'file://{abs_photo_path}'
        bg_path = os.path.abspath(os.path.join('static', "cards", 'flag.png'))

        html = del_btn(render_template(
            'card_base.html',
            name=name,
            email=email,
            phone=phone,
            job=job,
            photo=photo_url_file,
            bg_path=bg_path
        ).replace(f"<h2>{name}</h2>", new_name))

        # Транслитерованное безопасное имя
        safe_name = unidecode(name).replace(' ', '_')
        output_filename = f"Визитка_{safe_name}.png"

        html_path = f"static/cards/card_{photo.filename}.html"
        output_img = f"static/cards/{output_filename}"

        with open(html_path, "w") as f:
            f.write(html)

        render_html_to_image(html_path, output_img)

        download_url = url_for("download", filename=output_filename)
        card_url = url_for("static", filename=f"cards/{output_filename}")

        return render_template(
            'card.html',
            name=name,
            email=email,
            phone=phone,
            job=job,
            photo=url_for('static', filename='photoes/' + photo.filename),
            card=card_url,
            download_url=download_url
        ).replace(f"<h2>{name}</h2>", new_name)

    return render_template('form.html')


@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join('static/cards', filename)
    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    app.run(debug=True)


