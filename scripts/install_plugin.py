"""把仓库自带的 HTML-Preview 插件安装到某个 Obsidian 仓库（vault）。

用法（在本仓库根目录）：
    python scripts/install_plugin.py "你的 vault 路径"

做的事：
1. 把 plugins/html-preview/ 里的 main.js、manifest.json、styles.css 拷到
   <vault>/.obsidian/plugins/html-preview/
2. 在 <vault>/.obsidian/community-plugins.json 里登记 html-preview（已有则跳过）

装完请重启 Obsidian，并在 设置 → 第三方插件 里确认已关闭「受限模式」且开关是亮的。
"""
import json
import os
import shutil
import sys

PLUGIN_ID = "html-preview"
FILES = ["main.js", "manifest.json", "styles.css"]
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "plugins", PLUGIN_ID)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    vault = os.path.abspath(sys.argv[1])
    if not os.path.isdir(vault):
        sys.exit("找不到目录: " + vault)
    for name in FILES:
        if not os.path.isfile(os.path.join(SRC, name)):
            sys.exit("安装包缺少文件: " + os.path.join(SRC, name))

    obsidian = os.path.join(vault, ".obsidian")
    dst = os.path.join(obsidian, "plugins", PLUGIN_ID)
    os.makedirs(dst, exist_ok=True)
    for name in FILES:
        shutil.copy2(os.path.join(SRC, name), os.path.join(dst, name))
    print("已复制到 " + dst)

    registry = os.path.join(obsidian, "community-plugins.json")
    enabled = []
    if os.path.isfile(registry):
        with open(registry, encoding="utf-8") as f:
            try:
                enabled = json.load(f)
            except ValueError:
                sys.exit("community-plugins.json 不是合法的 JSON，请手动检查: " + registry)
    if PLUGIN_ID in enabled:
        print("community-plugins.json 里已经有 " + PLUGIN_ID)
    else:
        enabled.append(PLUGIN_ID)
        with open(registry, "w", encoding="utf-8") as f:
            json.dump(enabled, f, ensure_ascii=False, indent=2)
        print("已在 community-plugins.json 里登记 " + PLUGIN_ID)

    print("\n下一步：重启 Obsidian；设置 → 第三方插件 → 关闭受限模式并打开 HTML-Preview 的开关。")


if __name__ == "__main__":
    main()
