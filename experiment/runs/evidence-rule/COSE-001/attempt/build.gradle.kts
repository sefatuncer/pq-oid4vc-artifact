import org.jetbrains.kotlin.gradle.dsl.JvmTarget
plugins {
    kotlin("jvm") version "2.4.10"
    application
}
repositories { mavenCentral() }
dependencies {
    // target artifact, pinned version (same coordinate as the installation record)
    implementation("at.asitplus.signum:indispensable-cosef:3.26.0")
}
java { targetCompatibility = JavaVersion.VERSION_17; sourceCompatibility = JavaVersion.VERSION_17 }
kotlin { compilerOptions { jvmTarget.set(JvmTarget.JVM_17) } }
application { mainClass.set("MainKt") }
