import json
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path


class DonutAnnParser:
    json_tmp = {'file_name': None, 'ground_truth': '{"gt_parse": {ground_truth_parse}'}
    key_mask = {'p_id', 'gender', 'first_name', 'last_name', 'dob', 'date_of_issue', 'valid_through', 'place_of_birth'}

    def _gen_one_sample(self, ann):
        out = self.json_tmp.copy()
        out['file_name'] = ann['file_name']
        gt = dict()
        for k, v in ann['ground_truth'].items():
            if k not in self.key_mask:
                continue
            gt[k] = v['text']
        out['ground_truth'] = json.dumps({'gt_parse': gt})
        return json.dumps(out)

    def convert(self, in_file_path, out_file_path):
        out_f = open(out_file_path, 'w')
        with open(in_file_path, 'r') as in_f:
            for line in in_f.readlines():
                ann = json.loads(line)
                json_str = self._gen_one_sample(ann)
                out_f.write(json_str + '\n')


if __name__ == '__main__':
    parser = ArgumentParser(prog=f'python {Path(__file__).name}',
                            description='Convert annotations to Donut format.\n'
                                        'The generated metadata.jsonl will be placed under the same folder',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', '--folder', type=str, help='folder containing ground_truth.jsonl', required=True)
    args = parser.parse_args()
    work_dir = Path(args.folder)
    in_file = work_dir / 'ground_truth.jsonl'
    out_file = work_dir / 'metadata.jsonl'

    parser = DonutAnnParser()
    parser.convert(in_file, out_file)
