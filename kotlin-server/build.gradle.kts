import org.gradle.api.JavaVersion.VERSION_25
import org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_25
import org.jetbrains.kotlin.gradle.tasks.KotlinJvmCompile

plugins {
    alias(libs.plugins.kotlin.jvm)
    application
}


application {
    mainClass = "org.aaron.ServerKt"
}

repositories {
    mavenCentral()
}

tasks {
    withType<KotlinJvmCompile>().configureEach {
        compilerOptions {
            jvmTarget.set(JVM_25)
        }
    }

    withType<Test> {
        useJUnitPlatform()
    }

    java {
        sourceCompatibility = VERSION_25
        targetCompatibility = VERSION_25
    }
}

dependencies {
    implementation(libs.http4k.core)
    implementation(libs.http4k.server.helidon)
}

