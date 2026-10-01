# C3 adaptörü (JVM/Java): java-jwt 4.6.1, jjwt 0.13.0, authlete sd-jwt 1.9 (+ Nimbus 10.10). Sürümler pom.xml'de sabit.
FROM pq-a09-env-jvm:1.0 AS b
WORKDIR /w
COPY pom.xml /w/
COPY src /w/src
RUN mvn -q -B -Dmaven.test.skip=true package && mvn -q -B dependency:tree -DoutputFile=/w/dep-tree.txt
FROM pq-a09-env-jvm:1.0
COPY --from=b /w/target/adaptor.jar /w/dep-tree.txt /a/
COPY src/main/java/c3/Main.java /a/Main.java
ENTRYPOINT ["java", "-jar", "/a/adaptor.jar"]
