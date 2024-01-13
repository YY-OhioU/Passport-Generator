import json
import random
from argparse import ArgumentParser
from copy import copy, deepcopy
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw
from faker import Faker, providers
from tqdm import tqdm

Faker.seed(1591)
random.seed(1591)
CWD = Path(__file__).resolve().parent
faker = Faker()
faker.add_provider(providers.passport)

MARGIN = 5
BB_ADJUST = 5

TMP_NAME = 'MO_passport_text_removed'


class ImageGenerator:
    template_folder = CWD / 'assets' / 'template'
    font_folder = CWD / 'assets' / 'font'
    info_dict = {
        'type': 'P',
        'USA': 'USA',
        'p_id': '',
        'first_name': '',
        'last_name': '',
        'country_full': 'UNITED STATES OF AMERICA',
        'dob': '',
        'date_of_issue': '',
        'place_of_birth': '',
        'valid_through': '',
        'extra_information': '',
        'bar_line_one': '',
        'bar_line_two': '',
        'gender': '',
        'authority': 'United States'
    }

    def __init__(self, template_name, suffix='png'):
        self.template_name = template_name
        self.tmp_suffix = suffix
        self.tmp_res: tuple[int, int] = ()
        self.template: Image = None
        self.pos_dict: dict[str, tuple[float, float, float, float]] = {}
        self.font: ImageFont = None

        self.show_bb = False

        self.load_template()

    def load_template(self):
        self.font = ImageFont.truetype(str(self.font_folder / 'OCRB.otf'), 27)
        tmp_image = self.template_folder / f"{self.template_name}.{self.tmp_suffix}"
        self.template = Image.open(str(tmp_image))
        # self.template.load()
        self.tmp_res = self.template.size
        label_json = self.template_folder / f"{self.template_name}.json"

        with open(label_json, 'r') as f:
            j_obj = json.load(f)
            j_obj = j_obj[0]
            for entry in j_obj['annotations']:
                k = entry['label']
                cor = entry['coordinates']
                center = (cor['x'], cor['y'])
                w = cor['width']
                h = cor['height']
                self.pos_dict[k] = (center[0] - w / 2, center[1] - h / 2)

    def gen_image(self, num, out_dir):
        f = open(Path(out_dir) / "ground_truth.jsonl", 'w')
        for _ in tqdm(range(num)):
            info = self.get_info()
            out = f"output{_}.png"
            out_f = Path(out_dir) / out
            ground_truth = self.draw(info, out_f)
            anno = {'file_name': out, 'ground_truth': ground_truth}
            json_str = json.dumps(anno, ensure_ascii=True)
            f.write(f"{json_str}\n")
            # print(f"=========Done============")
        f.close()

    # Should Override for different type of data
    def get_info(self):

        info = copy(self.info_dict)
        pid = faker.passport_number()
        info['p_id'] = pid
        # gender = faker.passport_gender()  # faker sometimes gives 'X' as gender
        gender = random.choice(['M', 'F'])
        info['gender'] = gender
        name = faker.passport_owner(gender)
        info['first_name'], info['last_name'] = name
        dob = faker.passport_dob()
        info['dob'], info['date_of_issue'], info['valid_through'] = faker.passport_dates(dob)
        info['place_of_birth'] = f"{faker.administrative_unit().upper()},U.S.A"
        return info

    def draw_word(self, draw, start_pos, string):
        if string == '':
            print(f"string: {string}")
            return [1, 1, 1, 1]
        wbb = [*start_pos]
        pos = start_pos
        for sId in range(len(string)):
            s = string[sId]
            margin = MARGIN
            draw.text(pos, s, font=self.font, fill='black')
            bb = draw.textbbox(pos, s, self.font)
            # print(f"size for [{s}]: [{bb[2]-bb[0]}, {bb[3]-bb[1]}]")
            pos = [bb[2] - margin, pos[1]]
        wbb.extend([bb[2] - margin + BB_ADJUST, bb[3]])
        return wbb

    def draw(self, info, out):
        # if isinstance(out, Path):
        #     print(f"convert out to str")
        #     out = out.absolute().__str__()

        tmp = deepcopy(self.template)
        draw = ImageDraw.Draw(tmp)
        gt_dict = dict()
        for k, pos in self.pos_dict.items():
            actual_pos = [round(x) for x in pos]
            string = info[k]
            gt_dict[k] = {
                'text': string,
                'bb': None
            }
            if not string:
                # print(f"No content for key: {k}")
                continue

            #  old drawing
            # draw.text(actual_pos, string, font=self.font, fill='black')
            # bb = draw.textbbox(actual_pos, string, self.font)

            bb = self.draw_word(draw, actual_pos, string)
            gt_dict[k]['bb'] = bb

            if self.show_bb:
                poly = [
                    [bb[0], bb[1]],
                    [bb[0], bb[3]],
                    [bb[2], bb[3]],
                    [bb[2], bb[1]]
                ]

                draw.rectangle(bb, outline='red', width=1)

                colors = ['blue', 'black', 'green', 'yellow']
                for idx, p in enumerate(poly):
                    draw.point(p, fill=colors[idx])
        tmp.save(out)
        return gt_dict


if __name__ == '__main__':
    parser = ArgumentParser(
        prog=f'python {Path(__file__).name}',
        description='Generate fake passport images'
    )
    parser.add_argument('-n', '--number', type=int, help='num of images', default=3)
    parser.add_argument('-o', '--output', type=str, help='output directory', default='output')
    parser.add_argument('-b', '--bbox', action='store_true', help='show vertices of bounding boxes')
    args = parser.parse_args()
    count = args.number
    output_dir = Path(args.output).resolve()
    show_bb = args.bbox

    g = ImageGenerator(TMP_NAME)
    if show_bb:
        g.show_bb = True

    tmp_prefix = (Path(g.template_folder) / TMP_NAME).absolute()
    msg = f"Going to generate [{count}] samples in [{output_dir}]\n" \
          f"Template:\n\t{tmp_prefix}.png\n\t{tmp_prefix}.json"
    print(msg)
    print("Generating...")
    g.gen_image(count, output_dir)
