"""从 Obsidian vault 同步笔记到本仓库。

用法（在仓库根目录）：
    python scripts/sync_from_vault.py
    python scripts/sync_from_vault.py --vault "E:/obsidian/algorithmDesign_ideas"

做的事：
1. 把 vault 中「经典算法」目录下的笔记镜像到仓库（会删除仓库里已不存在于 vault 的笔记）。
2. 收集笔记里引用的图片（![[xxx.png]]），统一拷贝到仓库的 attachments/。
3. 把图片嵌入 ![[xxx.png|500]] 改写成标准 Markdown ![|500](相对路径)，
   这样 GitHub 和 Obsidian 都能显示。笔记之间的 [[双链]] 保持不变。
"""
import argparse
import os
import re
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VAULT = "E:/obsidian/algorithmDesign_ideas"
NOTES_SUBDIR = "学习与算法/算法练习/经典算法"

# 镜像的目录 / 文件（相对「经典算法」目录）
MANAGED = ["0.基础概念", "1.Patterns", "2.leetcodes", "算法整理.md"]
# 不发布的文件
EXCLUDE = {"未命名.md"}

ATTACH_DIR = "attachments"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
EMBED_RE = re.compile(r"!\[\[([^\]|#]+?)(?:\|([^\]]*))?\]\]")


def build_index(root):
    """basename -> 完整路径，模拟 Obsidian 按文件名解析链接。"""
    index = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            index.setdefault(name, os.path.join(dirpath, name))
    return index


def mirror(src_root):
    """把 MANAGED 里的内容复制到仓库，返回复制的 .md 文件列表（仓库内路径）。"""
    md_files = []
    for item in MANAGED:
        src = os.path.join(src_root, item)
        dst = os.path.join(REPO, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            md_files.append(dst)
            continue
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            rel = os.path.relpath(dirpath, src)
            out_dir = os.path.normpath(os.path.join(dst, rel))
            os.makedirs(out_dir, exist_ok=True)
            for name in filenames:
                if name in EXCLUDE:
                    continue
                out = os.path.join(out_dir, name)
                shutil.copy2(os.path.join(dirpath, name), out)
                if name.endswith(".md"):
                    md_files.append(out)
    return md_files


def rewrite_embeds(md_files, notes_index, vault_index):
    """改写图片嵌入，把仓库里没有的图片拷到 attachments/。返回找不到的图片。"""
    attach_root = os.path.join(REPO, ATTACH_DIR)
    if os.path.isdir(attach_root):
        shutil.rmtree(attach_root)
    os.makedirs(attach_root)
    repo_index = build_index(REPO)
    missing = set()

    for md in md_files:
        with open(md, encoding="utf-8") as f:
            text = f.read()

        def repl(m):
            target, size = m.group(1).strip(), m.group(2)
            name = os.path.basename(target)
            if not name.lower().endswith(IMAGE_EXT):
                return m.group(0)  # 嵌入的是笔记，保持双链
            if name in repo_index:
                path = repo_index[name]
            else:
                src = notes_index.get(name) or vault_index.get(name)
                if src is None:
                    missing.add(name)
                    return m.group(0)
                path = os.path.join(attach_root, name)
                shutil.copy2(src, path)
                repo_index[name] = path
            rel = os.path.relpath(path, os.path.dirname(md)).replace(os.sep, "/")
            alt = "|" + size if size else ""
            return "![%s](%s)" % (alt, rel.replace(" ", "%20"))

        new = EMBED_RE.sub(repl, text)
        if new != text:
            with open(md, "w", encoding="utf-8", newline="") as f:
                f.write(new)
    return missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vault", default=DEFAULT_VAULT)
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    src_root = os.path.join(args.vault, NOTES_SUBDIR)
    if not os.path.isdir(src_root):
        sys.exit("找不到笔记目录: " + src_root)

    md_files = mirror(src_root)
    missing = rewrite_embeds(md_files, build_index(src_root), build_index(args.vault))
    print("同步 %d 篇笔记，图片 %d 张" % (len(md_files), len(os.listdir(os.path.join(REPO, ATTACH_DIR)))))
    if missing:
        print("以下图片在 vault 中找不到：")
        for name in sorted(missing):
            print("  " + name)


if __name__ == "__main__":
    main()
