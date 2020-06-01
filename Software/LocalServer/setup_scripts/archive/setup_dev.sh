# removing vim
apt-get remove vim vim-tiny vim-runtime -y

# for configuring --with-x
apt-get install xorg xauth libx11-dev libxt-dev -y

# install updated vim
cd ~
git clone https://github.com/vim/vim.git
cd vim
./configure --with-x
make install
cd ~

# install vim-gtk for pasting:
sudo apt-get install vim-gtk -y # this may not work, also might need x11 libraries and :set clipboard=unnamed and :set clipboard=unnamedplus

# https://askubuntu.com/questions/347519/unable-to-copy-from-vim-to-system-clipboard
# https://stackoverflow.com/questions/3961859/how-to-copy-to-clipboard-in-vim

# setup environment for dev
git clone https://github.com/amckay1/vimrc.git $HOME/.vim_runtime
/bin/bash $HOME/.vim_runtime/install_awesome_vimrc.sh
cp $HOME/.vim_runtime/tmuxconfigfile $HOME/.tmux.conf

# consider mapping capslock to escape key: https://stackoverflow.com/questions/2176532/how-to-map-caps-lock-key-in-vim


