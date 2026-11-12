package vn.tiguan.parkedtube

import android.net.Uri

object YouTubeUrlParser {
    private val pattern = Regex("^[a-zA-Z0-9_-]{11}$")
    fun parse(value: String): String? {
        val v = value.trim()
        if (pattern.matches(v)) return v
        val uri = try {
            Uri.parse(if (v.startsWith("http")) v else "https://$v")
        } catch (_: Exception) { return null }
        if (uri.scheme != "https") return null
        val id = when (uri.host?.lowercase()) {
            "youtu.be", "www.youtu.be" -> uri.pathSegments.firstOrNull()
            "youtube.com", "www.youtube.com", "m.youtube.com" -> when(uri.pathSegments.firstOrNull()) {
                "watch" -> uri.getQueryParameter("v")
                "shorts", "live", "embed" -> uri.pathSegments.getOrNull(1)
                else -> null
            }
            else -> null
        }
        return id?.takeIf { pattern.matches(it) }
    }
}
