plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "vn.tiguan.parkedtube"
    compileSdk = 35
    defaultConfig {
        applicationId = "vn.tiguan.parkedtube"
        minSdk = 28
        targetSdk = 35
        versionCode = 1
        versionName = "1.0-alpha"
    }
    flavorDimensions += "projection"
    productFlavors {
        create("phone") {
            dimension = "projection"
            applicationIdSuffix = ".phone"
            resValue("string", "app_name", "ParkedTube Phone")
        }
        create("autoPreview") {
            dimension = "projection"
            applicationIdSuffix = ".preview"
            resValue("string", "app_name", "ParkedTube AA Preview")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
dependencies {
    implementation("androidx.webkit:webkit:1.12.1")
}
