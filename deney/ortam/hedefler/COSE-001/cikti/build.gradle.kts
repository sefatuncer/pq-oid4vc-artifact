plugins { java }
repositories { mavenCentral() }
dependencies { implementation("at.asitplus.signum:indispensable-cosef:3.26.0") }
tasks.register<Sync>("kopyala") { from(configurations.runtimeClasspath); into(layout.buildDirectory.dir("lib")) }
