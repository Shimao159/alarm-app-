# GitHub Actions 云端打包教程（零 Linux 操作）

全程在浏览器里点，不用装 Linux、不用装 WSL。打包机是 GitHub 免费的 Linux 服务器。

## 你只需做 4 步

### ① 注册 GitHub（免费）
打开 https://github.com ，点 Sign up，邮箱注册即可。

### ② 新建一个仓库（Repository）
1. 右上角 `+` → `New repository`
2. Repository name 填 `alarm-app`（随意）
3. **务必勾选 `Add a README file`**（否则首次 push 会失败）
4. 点 `Create repository`

### ③ 把项目文件上传到仓库
1. 进到刚建好的仓库页面
2. 点 `Add file` → `Upload files`
3. 把本文件夹里的 **4 个文件**拖进去：
   - `main.py`
   - `service.py`
   - `buildozer.spec`
   - `.github/workflows/build.yml`（含这个文件夹一起上传）
4. 往下拉，点 `Commit changes`

### ④ 触发打包
1. 仓库页面点上方 `Actions` 标签页
2. 左侧选 `Build Android APK`
3. 右边点 `Run workflow` → 再点一次 `Run workflow`
4. 等 20-40 分钟（首次要下载 SDK/NDK，约 8-10GB）

## 下载 APK

1. 打包完成后，该任务页往下拉，右侧 `Artifacts` 栏出现 `AlarmApp-APK`
2. 点它下载，解压得到 `AlarmApp-2.0-debug.apk`
3. 拷到任意安卓手机，点击安装即可

> 这个 apk 发给任何人、拷到任意多台手机都能装，对方不用装 Python。

## 以后改了代码怎么重新打包

改完代码，回到仓库页面：
1. 点进 `main.py`（或其他文件）
2. 点右上角铅笔图标 `Edit this file`
3. 改完点 `Commit changes`
4. 再到 `Actions` 页手动点 `Run workflow`，等 20-40 分钟重新出包

## 常见问题

**Q: 打包失败、报红字？**
进 `Actions` 页点进那次任务，把红色报错的完整文字复制给我，我帮你改 `buildozer.spec` 或代码。

**Q: 装到手机上锁屏不响？**
国产手机（华为/小米/OPPO/vivo）要去系统设置开：
`自启动` + `省电策略 → 无限制` + `允许后台活动`

**Q: 提示仓库未初始化？**
新建仓库时**必须勾选 Add a README file**，否则首次 push 会失败。
