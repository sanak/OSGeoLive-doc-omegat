#!/usr/bin/env python3

import argparse
import os
import re

PO_EXT = ".po"


def load_po_files(top_dir):
    po_files = {}
    for root, dirs, files in os.walk(top_dir, topdown=False):
        for file in files:
            if file.endswith(PO_EXT):
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, top_dir)
                with open(path) as f:
                    po_files[rel_path] = f.readlines()
            else:
                continue
    return po_files


def get_header_len(lines):
    header_len = lines.index('\n') if '\n' in lines else len(lines)
    return header_len


def wrap_msgstr_line(line):
    wrapped_lines = []
    match = re.match(r'^msgstr "(.*)"$', line)
    content = match.group(1)
    if len(content) >= 70:
        wrapped_lines.append('msgstr ""\n')
        while len(content) > 76:
            idx = content.rfind(' ', 0, 77)
            hyphen_idx = content.rfind('-', 0, 77)
            if hyphen_idx >= 0 and hyphen_idx > idx:
                idx = hyphen_idx
            if idx == 76:
                wrapped_lines.append('"' + content[0:idx] + '"\n')
                content = content[idx:]
            elif idx >= 0:
                wrapped_lines.append('"' + content[0:idx + 1] + '"\n')
                content = content[idx + 1:]
            else:
                idx = content.find(' ', 76)
                if idx > 0:
                    wrapped_lines.append('"' + content[0:idx] + '"\n')
                    content = content[idx:]
                else:
                    wrapped_lines.append('"' + content + '"\n')
                    content = ''
                    break
        if len(content) > 0:
            wrapped_lines.append('"' + content + '"\n')
    else:
        wrapped_lines.append(line)
    return wrapped_lines


def main(args):
    # Load source/target po files
    source_po_files = load_po_files(args.source)
    target_po_files = load_po_files(args.target)

    # Format target catalogs
    for path in source_po_files:
        source_lines = source_po_files[path]
        source_path = os.path.join(args.source, path)
        if path in target_po_files:
            target_path = os.path.join(args.target, path)
            print(target_path)
            target_lines = target_po_files[path]

            source_header_len = get_header_len(source_lines)
            target_header_len = get_header_len(target_lines)
            if source_lines[0:source_header_len] == target_lines[0:target_header_len]:
                print("Already formatted")
                continue

            final_lines = source_lines[0:source_header_len]
            for target_line in target_lines[target_header_len:]:
                if target_line.startswith('msgstr '):
                    final_lines.extend(wrap_msgstr_line(target_line))
                else:
                    final_lines.append(target_line)

            with open(target_path, mode='w') as f:
                f.writelines(final_lines)

    print("Completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Format target files')
    parser.add_argument('source', nargs='?', default='./source',
                        help="A source directory to compare (default is './source')")
    parser.add_argument('target', nargs='?', default='./target',
                        help="A target directory to format (default is './target')")
    args = parser.parse_args()
    main(args)
