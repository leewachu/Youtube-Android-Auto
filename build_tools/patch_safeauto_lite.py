#!/usr/bin/env python3
"""
SafeAuto Lite:
- Web browser + YouTube TV interface for Android Auto
- no Shizuku, root, ADB or developer options needed at runtime
- no screen projection, Accessibility, or overlay permissions
Base source: iAlias/AASuite (MIT) @ e449095fa56269c091a6bc16b08c0dad72b14bb5.
This is an experimental proof of concept. It may not be shown by all AA hosts.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
p = root / 'app/build.gradle.kts'
b = p.read_text()
assert b.count('applicationId = "com.viami.aamirror"') == 1
b = b.replace('applicationId = "com.viami.aamirror"', 'applicationId = "app.safeauto.lite"')
assert b.count('versionCode = 9') == 1
b = b.replace('versionCode = 9', 'versionCode = 10')
assert b.count('versionName = "0.9"') == 1
b = b.replace('versionName = "0.9"', 'versionName = "1.0"')
p.write_text(b)

p = root / 'app/src/main/AndroidManifest.xml'
s = p.read_text()
for permission in [
    'android.permission.FOREGROUND_SERVICE',
    'android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION',
    'android.permission.POST_NOTIFICATIONS',
    'android.permission.SYSTEM_ALERT_WINDOW',
]:
    before = '<uses-permission android:name="' + permission + '" />'
    assert s.count(before) == 1, permission
    s = s.replace(before, '')
s, n = re.subn(r'\s*<uses-permission android:name="android.permission.WRITE_SETTINGS"\s*tools:ignore="ProtectedPermissions"\s*/>', '', s, count=1)
assert n == 1
import xml.etree.ElementTree as ET
ET.register_namespace('android', 'http://schemas.android.com/apk/res/android')
ET.register_namespace('tools', 'http://schemas.android.com/tools')
manifest_root = ET.fromstring(s)
application = manifest_root.find('application')
android_name = '{http://schemas.android.com/apk/res/android}name'
obsolete = {'.mirror.MirrorService', '.input.MirrorAccessibilityService'}
matching = [service for service in application.findall('service') if service.get(android_name) in obsolete]
assert len(matching) == 2, [node.get(android_name) for node in matching]
for service in matching:
    application.remove(service)
s = ET.tostring(manifest_root, encoding='unicode')
assert 'accessibilityservice' not in s.lower()
assert 'mediaProjection' not in s
assert 'shizuku' not in s.lower()
p.write_text(s)

p = root / 'app/src/main/java/com/viami/aamirror/car/HomeScreen.kt'
s = p.read_text()
block = '''        Mode(R.string.menu_mirror, R.string.menu_mirror_short, R.drawable.ic_app) {
            screenManager.push(MirrorScreen(carContext))
        },
'''
assert s.count(block) == 1
p.write_text(s.replace(block, ''))

p = root / 'app/src/main/java/com/viami/aamirror/car/SettingsScreen.kt'
s = p.read_text()
assert s.count('            .addItem(rotationRow())') == 1
p.write_text(s.replace('            .addItem(rotationRow())\n', ''))

# Prevent a network listener from starting on the connected phone.
p = root / 'app/src/main/java/com/viami/aamirror/car/MirrorSession.kt'
p.write_text('''package com.viami.aamirror.car

import android.content.Intent
import androidx.car.app.Screen
import androidx.car.app.Session

class MirrorSession : Session() {
    override fun onCreateScreen(intent: Intent): Screen = HomeScreen(carContext)
}
''')

# Replace setup page so users are not asked for screen recording, Accessibility
# service, overlay, debugging or extra permissions.
p = root / 'app/src/main/java/com/viami/aamirror/setup/SetupActivity.kt'
p.write_text('''package com.viami.aamirror.setup

import android.os.Bundle
import android.app.Activity
import android.graphics.Color
import android.view.Gravity
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView
import android.content.Intent

class SetupActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        title = "SafeAuto Lite"

        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(32, 56, 32, 32)
            setBackgroundColor(Color.rgb(245, 247, 250))
        }
        val heading = TextView(this).apply {
            text = "SafeAuto Lite 1.0"
            textSize = 26f
            setTextColor(Color.rgb(20, 26, 38))
        }
        root.addView(heading)
        val info = TextView(this).apply {
            text = "YouTube TV and Browser on Android Auto. No Shizuku, ADB, root, Accessibility, or screen recording required.\\n\\nConnect to Android Auto, then open SafeAuto Lite from the car launcher. Choose YouTube or Browser.\\n\\nCar launcher visibility depends on Android Auto's app installation restrictions. Video should only be used while parked.\\n\\nBank apps may independently apply their own security policies."
            textSize = 16f
            setTextColor(Color.rgb(48, 60, 78))
            setPadding(0, 20, 0, 24)
        }
        root.addView(info)
        val bookmarks = Button(this).apply {
            text = "Manage bookmarks"
            setOnClickListener {
                startActivity(Intent(this@SetupActivity, BookmarksActivity::class.java))
            }
        }
        root.addView(bookmarks, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT
        ))
        setContentView(root)
    }
    companion object {
        // Retained only for compilation of legacy unused mirroring classes.
        const val EXTRA_REQUEST_CAPTURE = "request_capture"
    }
}
''')

p = root / 'app/src/main/res/values/strings.xml'
s = p.read_text()
assert s.count('<string name="app_name">AA Suite</string>') == 1
p.write_text(s.replace('<string name="app_name">AA Suite</string>', '<string name="app_name">SafeAuto Lite</string>'))

assets = root / 'app/src/main/assets'
assets.mkdir(parents=True, exist_ok=True)
(assets / 'LICENSE_AASUITE.txt').write_text((root / 'LICENSE').read_text())
(root / 'SAFEAUTO_LITE_NOTICE.md').write_text('''# SafeAuto Lite 1.0 (experimental)
Built from iAlias/AASuite, commit e449095fa56269c091a6bc16b08c0dad72b14bb5.
Original software copyright (c) 2026 iAlias, licensed MIT (LICENSE retained).
Modifications: distinct application ID, new setup screen, home menu limited to
YouTube TV and browser, removed screen capture service, Accessibility service,
overlays/brightness/notification permission requests and LAN HTTP server.
No Shizuku or ADB required at runtime. INTERNET is needed by WebView.
Not an official Google/YouTube app; website capabilities may change.
Android Auto launcher visibility can require a Play-install provenance route.
Do not use video while driving. No guarantee of TPBank compatibility.
''')
print("SafeAuto Lite source ready, no Shizuku / ADB / Accessibility service")
