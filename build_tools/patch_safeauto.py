#!/usr/bin/env python3
"""Fork GitMag/AnyAuto GPL-3.0 from pinned v0.10 with offline SafeAuto identity."""
from pathlib import Path
import sys, re
root = Path(sys.argv[1])
old = 'com.mag.anyauto'
new = 'app.safeauto.mirror'
main_path = root / 'src/com/mag/anyauto/MainActivity.java'
manifest_path = root / 'AndroidManifest.xml'
build_path = root / 'build.sh'
label_path = root / 'res/values/strings.xml'
s = main_path.read_text()

def once(a,b):
    global s
    assert s.count(a)==1, ('Missing or duplicate upstream anchor',a,s.count(a))
    s=s.replace(a,b,1)

def remove_block(anchor):
    global s
    assert s.count(anchor)==1, (anchor,s.count(anchor))
    start=s.index(anchor)
    depth=0
    opening=s.index('{',start)
    quote=None
    escaped=False
    in_line=False
    in_block=False
    for i in range(opening,len(s)):
        c=s[i]; following=s[i+1] if i+1<len(s) else ''
        if in_line:
            if c=='\n': in_line=False
        elif in_block:
            if c=='*' and following=='/': in_block=False
        elif quote:
            if escaped: escaped=False
            elif c=='\\': escaped=True
            elif c==quote: quote=None
        elif c=='/' and following=='/': in_line=True
        elif c=='/' and following=='*': in_block=True
        elif c in ('"',"'"): quote=c
        elif c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0:
                end=i+1
                if end<len(s) and s[end]=='\n': end+=1
                s=s[:start]+s[end:]
                return
    raise RuntimeError('unterminated if block')

once('MENU_AUTO_UPDATE = 6, MENU_CHECK_UPDATE = 7, MENU_NAV_SIDE = 8;', 'MENU_NAV_SIDE = 8;')
once('        // only here, while AnyAuto is open; skipped when turned off or checked within the hour\n        Updater.check(this, false, r -> refresh());\n','')
once('        menu.add(0, MENU_AUTO_UPDATE, 4, "Check for updates automatically").setCheckable(true)\n                .setChecked(Prefs.autoUpdate(this));\n        menu.add(0, MENU_CHECK_UPDATE, 5, "Check for updates now");\n','')
remove_block('        if (item.getItemId() == MENU_AUTO_UPDATE) {')
remove_block('        if (item.getItemId() == MENU_CHECK_UPDATE) {')
once('        String update = Updater.readyVersion(this);\n','')
remove_block('        if (update != null) {')
assert 'Updater.' not in s and 'MENU_AUTO_UPDATE' not in s and 'MENU_CHECK_UPDATE' not in s
main_path.write_text(s)
(root / 'src/com/mag/anyauto/Updater.java').unlink()
manifest=manifest_path.read_text()
assert manifest.count('    <uses-permission android:name="android.permission.INTERNET" />\n')==1
manifest=manifest.replace('    <uses-permission android:name="android.permission.INTERNET" />\n','')
pattern=r'(?m)^        <!-- hands a downloaded update to UnknownAuto.*?^        </provider>\n'
manifest,n=re.subn(pattern,'',manifest,flags=re.S)
assert n==1,("FileProvider removal failed",n)
manifest_path.write_text(manifest)
b=build_path.read_text()
for before,after in [('APP_ID=com.mag.anyauto','APP_ID='+new),('VERSION_CODE=10','VERSION_CODE=11'),('VERSION_NAME=0.10','VERSION_NAME=0.10.1'),('APK=anyauto.apk','APK=safeauto.apk')]:
    assert b.count(before)==1,(before,b.count(before))
    b=b.replace(before,after,1)
b=b.replace('src/com/mag/anyauto/', 'src/app/safeauto/mirror/')
b=b.replace('Lcom/mag/anyauto/', 'Lapp/safeauto/mirror/')
build_path.write_text(b)
label=label_path.read_text()
assert '<string name="app_name">AnyAuto</string>' in label
label_path.write_text(label.replace('<string name="app_name">AnyAuto</string>', '<string name="app_name">SafeAuto</string>'))
for p in root.rglob('*'):
    if p.is_file() and p.suffix in ('.java','.aidl','.xml','.sh','.md','.txt','.py'):
        before=p.read_text()
        after=before.replace(old,new)
        if p.suffix=='.java':
            after=re.sub(r'"(?:\\.|[^"\\])*"',lambda m: m.group().replace('AnyAuto ','SafeAuto ').replace('"AnyAuto"','"SafeAuto"'),after)
        if after!=before:p.write_text(after)
source=root / 'src/com/mag/anyauto'
dest=root / 'src/app/safeauto/mirror'
dest.parent.mkdir(parents=True,exist_ok=True)
source.rename(dest)
assert 'android.permission.INTERNET' not in manifest_path.read_text()
assert 'Updater.' not in '\n'.join(x.read_text() for x in root.rglob('*.java'))
(root/'SAFEAUTO_NOTICE.md').write_text('# SafeAuto 0.10.1\nFork of GitMag/AnyAuto, copyright 2026 GitMag, GPL-3.0. See LICENSE.\nSource revision: 9ac39706b79d971ec592e360b137ae308eba36b8\nChanges: new app identifier, update checker removed, Internet permission removed.\nRequires Shizuku with shell privileges; no security guarantee.\n')
print('SafeAuto patched: offline app with package',new)
