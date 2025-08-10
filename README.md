
# 声明

该工具仅供学习交流使用，请勿用于商业用途，请在下载后24小时内删除

# bdo-fish

## 问就是封，用就别怕，怕就别用！

黑色沙漠钓鱼工具

## 安装

pip install -r requirements.txt

## 运行

python main_window.py

# build



nuitka --standalone --onefile --windows-uac-admin  --windows-console-mode=disable --plugin-enable=tk-inter --windows-console-mode=disable ./main_window.py --output-filename=钓鱼助手  --include-data-dir=./assets=assets --windows-icon-from-ico=./assets/logo.ico