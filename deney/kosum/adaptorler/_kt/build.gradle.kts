// İki ayrı derleme: -Pt=cose (COSE-001) ve -Pt=sdjwt (SDJWT-001). Ayrı imajlar, böylece vck kendi Signum sürümlerini çözer.
plugins { kotlin("jvm") version "2.4.10"; application }
repositories { mavenCentral() }
val t = (findProperty("t") ?: "cose").toString()
dependencies {
  if (t == "cose") {
    implementation("at.asitplus.signum:indispensable-cosef-jvm:3.26.0")
    implementation("at.asitplus.signum:supreme-jvm:0.16.0")
  } else {
    implementation("at.asitplus.wallet:vck-jvm:7.0.1")
  }
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
}
sourceSets { main { kotlin.srcDirs("src/common/kotlin", "src/$t/kotlin") } }
// JVM 24 hedefi; JDK 25 ile derlenir (Signum 3.26 meta verisi Kotlin 2.4 ister).
java { sourceCompatibility = JavaVersion.VERSION_24; targetCompatibility = JavaVersion.VERSION_24 }
kotlin { compilerOptions { jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_24) } }
application { mainClass.set("c3.MainKt"); applicationName = "kt-adaptor" }
