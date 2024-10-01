import os

deps = "build-essential git python3 python3-docutils liblua5.2-dev libass-dev libjpeg-dev \
libx264-dev libfdk-aac-dev libmpv-dev yasm libxcb-shm0-dev \
gcc g++ yasm git ninja-build autoconf \
libx11-dev libxext-dev libxv-dev libvdpau-dev libgl1-mesa-dev \
libasound2-dev libpulse-dev libfribidi-dev libfreetype6-dev \
libfontconfig1-dev libjpeg-dev libssl-dev libgnutls28-dev \
libx264-dev libmp3lame-dev libfdk-aac-dev mingw-w64"

os.system(f"sudo apt update && sudo apt install -y {deps}")


os.system("pip install meson")

os.system("git clone https://github.com/mpv-player/mpv-build.git")

os.chdir("mpv-build")

with open("ffmpeg_options", "w") as f:
    f.write("""
--enable-static
--disable-shared
--enable-pic
--disable-doc
--disable-debug
--enable-libx264
--enable-libmp3lame
--enable-libfdk-aac
--enable-nonfree
""")
    
with open("mpv_options", "w") as f: 
    f.write("""-Dlibmpv=true
-Dvdpau=disabled
-Dx11=disabled
-Dgl-x11=disabled
-Dvaapi-x11=disabled
""")
    

os.environ["CC"] = "x86_64-w64-mingw32-gcc"

os.system("./rebuild -j$(nproc)")
os.system("sudo ./install")
os.system("export PKG_CONFIG_PATH=$(pwd)/build_libs/lib/pkgconfig:$PKG_CONFIG_PATH")