plugins { java }
repositories { mavenCentral() }
dependencies { implementation("at.asitplus.wallet:vck:7.0.1") }
tasks.register<Sync>("kopyala") { from(configurations.runtimeClasspath); into(layout.buildDirectory.dir("lib")) }
