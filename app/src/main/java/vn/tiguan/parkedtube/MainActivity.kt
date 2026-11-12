package vn.tiguan.parkedtube

import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.view.ViewGroup
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import java.net.URLEncoder
import androidx.webkit.WebViewAssetLoader
import android.annotation.SuppressLint

class MainActivity : Activity() {
    private lateinit var web: WebView
    private lateinit var field: EditText
    private lateinit var parked: CheckBox
    private lateinit var status: TextView
    private var videoPage = false
    private val loader by lazy {
        WebViewAssetLoader.Builder().addPathHandler(
            "/assets/", WebViewAssetLoader.AssetsPathHandler(this)
        ).build()
    }
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(state: Bundle?) {
        super.onCreate(state)
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        layout.setBackgroundColor(Color.rgb(12,18,29))
        val label = TextView(this).apply {
            text = "ParkedTube V1  |  Tiguan 2019"
            textSize = 20f
            setTextColor(Color.WHITE)
            setPadding(16,16,16,8)
        }
        layout.addView(label)
        parked = CheckBox(this).apply {
            text = "Tôi xác nhận xe đang đỗ an toàn"
            setTextColor(Color.WHITE)
        }
        layout.addView(parked)
        field = EditText(this).apply {
            hint = "Dán URL YouTube hoặc nhập từ khóa"
            setSingleLine()
            setTextColor(Color.WHITE)
            setHintTextColor(Color.LTGRAY)
        }
        layout.addView(field)
        val buttons = LinearLayout(this)
        val play = Button(this).apply {
            text = "Phát video"
            setOnClickListener {
                if (!parked.isChecked) return@setOnClickListener
                val id = YouTubeUrlParser.parse(field.text.toString())
                if (id != null) {
                    videoPage = true
                    web.loadUrl("https://appassets.androidplatform.net/assets/player.html?v=$id")
                    status.text = "Đã tải trình phát; chạm Play để phát"
                } else status.text = "Vui lòng nhập URL YouTube hợp lệ"
            }
        }
        val search = Button(this).apply {
            text = "Tìm trên YouTube"
            setOnClickListener {
                if (!parked.isChecked) return@setOnClickListener
                pause()
                videoPage = false
                val q = URLEncoder.encode(field.text.toString(), "UTF-8")
                web.loadUrl("https://www.youtube.com/results?search_query=$q")
            }
        }
        buttons.addView(play, LinearLayout.LayoutParams(0,-2,1f))
        buttons.addView(search, LinearLayout.LayoutParams(0,-2,1f))
        layout.addView(buttons)
        parked.setOnCheckedChangeListener { _, checked ->
            play.isEnabled = checked
            search.isEnabled = checked
            if (!checked) {
                pause()
                web.loadUrl("https://appassets.androidplatform.net/assets/welcome.html")
                videoPage = false
            }
        }
        play.isEnabled = false
        search.isEnabled = false
        status = TextView(this).apply {
            setTextColor(Color.LTGRAY)
            text = "Chỉ sử dụng khi xe đã đỗ."
        }
        layout.addView(status)
        web = WebView(this)
        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.settings.mediaPlaybackRequiresUserGesture = true
        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView?, request: WebResourceRequest) =
                loader.shouldInterceptRequest(request.url) ?: super.shouldInterceptRequest(view, request)
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest): Boolean {
                if (!request.isForMainFrame) return false
                val id = YouTubeUrlParser.parse(request.url.toString())
                if (id != null) {
                    if (parked.isChecked) {
                        videoPage = true
                        web.loadUrl("https://appassets.androidplatform.net/assets/player.html?v=$id")
                    }
                    return true
                }
                return request.url.scheme != "https"
            }
        }
        web.webChromeClient = object : WebChromeClient() {}
        layout.addView(web, LinearLayout.LayoutParams(-1,0,1f))
        setContentView(layout)
        web.loadUrl("https://appassets.androidplatform.net/assets/welcome.html")
        handleShare(intent)
    }
    private fun handleShare(incoming: Intent?) {
        if (incoming?.action != Intent.ACTION_SEND) return
        val raw = incoming.getStringExtra(Intent.EXTRA_TEXT).orEmpty()
        val matched = Regex("https?://[^\\s]+").find(raw)?.value ?: raw
        val id = YouTubeUrlParser.parse(matched)
        if (id != null) field.setText("https://youtu.be/$id")
    }
    override fun onNewIntent(newIntent: Intent) {
        super.onNewIntent(newIntent)
        setIntent(newIntent)
        handleShare(newIntent)
    }
    private fun pause() {
        if (::web.isInitialized && videoPage)
            web.evaluateJavascript("window.pauseYoutube && window.pauseYoutube();", null)
    }
    override fun onPause() {
        pause()
        if (::web.isInitialized) web.onPause()
        super.onPause()
    }
    override fun onResume() {
        super.onResume()
        if (::web.isInitialized) web.onResume()
    }
    override fun onDestroy() {
        pause()
        if (::web.isInitialized) {
            (web.parent as? ViewGroup)?.removeView(web)
            web.destroy()
        }
        super.onDestroy()
    }
}
