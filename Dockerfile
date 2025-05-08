# 1. پایه: Microsoft Build of OpenJDK روی CBL-Mariner 2.0
FROM mcr.microsoft.com/openjdk/jdk:11-mariner

# 2. نصب پیش‌نیازهای اصلی
RUN tdnf update -y && tdnf install -y \
    python3 python3-pip python3-setuptools make gcc git \
    libffi-devel libjpeg-turbo libjpeg-turbo-devel \
    blas-devel lapack-devel \
    zlib-devel cmake mesa-libEGL mesa-libGLES \
    freetype freetype-devel curl unzip \
    libpng libpng-devel \
    gdk-pixbuf2-devel && \
    tdnf clean all

# 3. نصب Buildozer و Cython
RUN pip3 install --upgrade pip setuptools wheel \
 && pip3 install buildozer Cython

# 4. دانلود و نصب Android SDK Command-line Tools
RUN mkdir -p /root/.buildozer \
 && curl -L https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip \
       -o /root/.buildozer/cmdline-tools.zip \
 && unzip /root/.buildozer/cmdline-tools.zip -d /root/.buildozer/ \
 && rm /root/.buildozer/cmdline-tools.zip

# 5. تنظیم متغیرهای محیطی SDK/NDK
ENV ANDROID_HOME=/root/.buildozer
ENV PATH=$PATH:$ANDROID_HOME/cmdline-tools/bin:$ANDROID_HOME/platform-tools

# 6. قبول خودکار لایسنس‌ها و نصب platform-tools, build-tools, NDK
RUN yes | sdkmanager --sdk_root=$ANDROID_HOME --licenses \
 && yes | sdkmanager --sdk_root=$ANDROID_HOME "platform-tools" \
     "platforms;android-29" "build-tools;29.0.3" \
 && yes | sdkmanager --sdk_root=$ANDROID_HOME "ndk;21.4.7075529"

# 7. کپی پروژه و تنظیم مسیر کاری
WORKDIR /workspace
COPY . /workspace

# 8. فرمان پیش‌فرض: ساخت APK در حالت debug
CMD ["buildozer", "android", "debug"]
