#!/bin/sh
# This file was auto-generated
if [ -z $1 ];
then
echo "Please spacify the backend url"
exit 1
fi

echo "Importing CVE-2018-8039 (1 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8039 -r https://github.com/apache/cxf/ -e fae6fabf9bd7647f5e9cb68897a7d72b545b741:3.2.5,8ed6208f987ff72e4c4d2cf8a6b1ec9b27575d4:3.1.16  -descr "Description:   A vulnerability was reported in Apache CXF. A remote user can bypass TLS hostname verification in certain cases.The system does not properly verify TLS hostnames when used with the 'com.sun.net.ssl' implementation. A remote user that can conduct a man-in-the-middle attack can bypass the hostname verification.Impact:   A remote user can bypass TLS hostname verification.Solution:   The vendor has issued a fix (3.1.16, 3.2.5)." -links "https://cxf.apache.org/security-advisories.html,https://securitytracker.com/id/1041199"  -sie -u

echo "Importing CVE-2016-2415 (2 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2415 -r https://android.googlesource.com/platform/packages/apps/Exchange -e 0d1a38b1755efe7ed4e8d7302a24186616bba9b2  -sie -u

echo "Importing S2-043 (3 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b S2-043 -r https://github.com/apache/struts -e ba0563183b128dcef88b469f46e528a12e0179e7  -descr "Usage of the Config Browser in a production environment can lead to exposing vunerable information of the application. Please read out Security guideline and restrict access to the Config Browwser or do not use in a production environment!" -links "https://cwiki.apache.org/confluence/display/WW/S2-043"  -sie -u

echo "Importing CVE-2017-12611 (4 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12611 -r https://github.com/apache/struts -e 2306f5f7fad7f0157f216f34331238feb0539fa:support-2-3,637ad1c3707266c33daabb18d7754e795e6681f:master  -descr "A possible Remote Code Execution attack when using an unintentional expression in Freemarker tag instead of string literals." -links "https://cwiki.apache.org/confluence/display/WW/S2-053"  -sie -u

echo "Importing HADOOP-12751 (5 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-12751 -r https://github.com/apache/hadoop/ -e 829a2e4d271f05afb209ddc834cd4a0e85492ed:3.1,d13cd394e553a1ffe74ccfb5bc4032409c4e5c3:2.8,092b1997418c8042224d24751a8fdde7d39a9ed:2.9,d2531df1e87064be388e6fa6cb85f3729e87a2f:2.7  -descr "While using kerberos Hadoop incorrectly assumes names with '@' to be non-simple. Description: In the scenario of a trust between two directories, eg. FreeIPA (ipa.local) and Active Directory (ad.local) users can be made available on the OS level by something like sssd. The trusted users will be of the form 'user@ad.local' while other users are will not contain the domain. Executing 'id -Gn user@ad.local' will successfully return the groups the user belongs to if configured correctly. However, it is assumed by Hadoop that users of the format with '@' cannot be correct. This code is in KerberosName.java and seems to be a validator if the 'auth_to_local' rules are applied correctly. In my opinion this should be removed or changed to a different kind of check or maybe logged as a warning while still proceeding, as the current behavior limits integration possibilities with other standard tools. Workaround are difficult to apply (by having a rewrite by system tools to for example user_ad_local) due to down stream consequences. Fixed Version/s: 2.8.0, 3.0.0-alpha1, 2.7.6" -links "https://issues.apache.org/jira/browse/HADOOP-12751,http://hadoop.apache.org/docs/r2.7.6/hadoop-project-dist/hadoop-common/releasenotes.html"  -sie -u

echo "Importing CVE-2018-12537 (6 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12537 -r https://github.com/eclipse/vert.x -e 1bb6445226c39a95e7d07ce3caaf56828e8aab72  -sie -u

echo "Importing CVE-2018-1000112 (7 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000112 -r https://github.com/jenkinsci/mercurial-plugin -e 54b4f82e80c89d51b12bc64258f6b59e98b0c16a  -sie -u

echo "Importing CVE-2018-12691 (8 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12691 -r https://github.com/opennetworkinglab/onos/ -e 4b931a988e2f6b547769ba70c815aaea4fe6b5d0  -descr "Time-of-check to time-of-use (TOCTOU) race condition in org.onosproject.acl (aka the access control application) in ONOS v1.13 and earlier allows attackers to bypass network access control via data plane packet injection." -links "https://snyk.io/vuln/SNYK-JAVA-ORGONOSPROJECT-32423,https://wiki.onosproject.org/display/ONOS/Security+advisories"  -sie -u

echo "Importing CVE-2014-0054 (9 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0054 -r https://github.com/spring-projects/spring-framework -e 1c5cab2a4069ec3239c531d741aeb07a434f521b,edba32b3093703d5e9ed42b5b8ec23ecc1998398  -sie -u

echo "Importing CVE-2017-7536 (10 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7536 -r https://github.com/hibernate/hibernate-validator/ -e 0778a5c98b817771a645c6f4ba0b28dd8b5437b:5.4,0ed45f37c4680998167179e631113a2c9cb5d11:5.2,0886e89900d343ea20fde5137c9a3086e6da9ac:5.3  -links "https://bugzilla.redhat.com/show_bug.cgi?id=1465573,https://access.redhat.com/security/cve/cve-2017-7536,https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=885577"  -sie -u

echo "Importing CVE-2017-2638 (11 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-2638 -r https://github.com/infinispan/infinispan/ -e f2d54c4ecb75c7264d4160ca7c461135712201a9  -links "https://snyk.io/vuln/SNYK-JAVA-ORGINFINISPAN-32418,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2638,https://issues.jboss.org/browse/ISPN-7485"  -sie -u

echo "Importing CVE-2013-7330 (12 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7330 -r https://github.com/jenkinsci/jenkins -e 36342d71e29e0620f803a7470ce96c61761648d8  -sie -u

echo "Importing CVE-2010-1244 (13 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2010-1244 -r https://github.com/apache/activemq -e 1f464b9412e1b1c08d40c8ffac40edd52731da48  -sie -u

echo "Importing CVE-2018-1000864 (14 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000864 -r https://github.com/jenkinsci/jenkins/ -e 73afa0ca786a87f05b5433e2e38f863826fcad17  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-72668,https://jenkins.io/security/advisory/2018-12-05/#SECURITY-1193"  -sie -u

echo "Importing CVE-2018-17187 (15 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17187 -r https://github.com/apache/qpid-proton-j/ -e 0cb8ca03cec42120dcfc434561592d89a89a805e  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEQPID-72605,https://issues.apache.org/jira/browse/PROTON-1962,https://mail-archives.apache.org/mod_mbox/qpid-users/201811.mbox/%3CCAFitrpQSV73Vz7rJYfLJK7gvEymZSCR5ooWUeU8j4jzRydk-eg%40mail.gmail.com%3E"  -sie -u

echo "Importing CVE-2018-11307 (16 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11307 -r https://github.com/FasterXML/jackson-databind/ -e 051bd5e447fbc9539e12a4fe90eb989dba0c656:2.8.11.2,27b4defc270454dea6842bd9279f17387eceb73:2.7.9.4  -descr "Potential information exfiltration with default typing, serialization gadget from MyBatis. Description: A new potential gadget type from MyBatis (https://github.com/mybatis/mybatis-3) has been reported. It may allow content exfiltration (remote access by sending contents over ftp) when untrusted content is deserialized with default typing enabled. Versions 2.9.5, 2.8.11.1, 2.7.9.3 (as well as earlier minor versions) are affected." -links "https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.8,https://github.com/FasterXML/jackson-databind/issues/2032"  -sie -u

echo "Importing CVE-2016-0768 (17 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0768 -r https://github.com/tada/pljava -e 675254b0f17b76f05e72cba2e3b8d3e548ae7a43  -sie -u

echo "Importing CVE-2018-1000114 (18 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000114 -r https://github.com/jenkinsci/promoted-builds-plugin -e 9b99b9427cc4f692644f929e70f3e7b2180b11c5  -sie -u

echo "Importing CVE-2018-18389 (19 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-18389 -r https://github.com/neo4j/neo4j/ -e 46de5d01ae2741ffe04c36270fc62c6d490f65c9  -links "https://snyk.io/vuln/SNYK-JAVA-ORGNEO4J-72466,https://github.com/neo4j/neo4j/issues/12047"  -sie -u

echo "Importing CVE-2016-1000338 (20 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000338 -r https://github.com/bcgit/bc-java -e 843c2e60f67d71faf81d236f448ebbe56c62c647  -descr "DSA does not fully validate ASN.1 encoding of signature on verification. It is possible to inject extra elements in the sequence making up the signature and still have it validate, which in some cases may allow the introduction of invisible data into a signed structure." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2018-1273 (21 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1273 -r https://github.com/spring-projects/spring-data-commons/ -e ae1dd2741ce06d44a0966ecbd6f47beabde2b65:2.0.x,b1a20ae1e82a63f99b3afc6f2aaedb3bf4dc432:1.13.x  -descr "Spring Data Commons, versions prior to 1.13 to 1.13.10, 2.0 to 2.0.5, and older unsupported versions, contain a property binder vulnerability caused by improper neutralization of special elements. An unauthenticated remote malicious user (or attacker) can supply specially crafted request parameters against Spring Data REST backed HTTP resources or using Spring Datas projection-based request payload binding hat can lead to a remote code execution attack. Affected : Spring Data Commons 1.13 to 1.13.10 (Ingalls SR10), Spring Data REST 2.6 to 2.6.10 (Ingalls SR10), Spring Data Commons 2.0 to 2.0.5 (Kay SR5), Spring Data REST 3.0 to 3.0.5 (Kay SR5), Older unsupported versions are also affected." -links "https://pivotal.io/security/cve-2018-1273"  -sie -u

echo "Importing CVE-2018-14637 (22 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-14637 -r https://github.com/keycloak/keycloak/ -e 0fe0b875d63cce3d2855d85d25bb8757bce13eb1  -links "https://snyk.io/vuln/SNYK-JAVA-ORGKEYCLOAK-72652,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14637"  -sie -u

echo "Importing CVE-2016-1000340 (23 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000340 -r https://github.com/bcgit/bc-java -e 790642084c4e0cadd47352054f868cc8397e2c00  -descr "Static ECDH vulnerable to carry propagation bug. Carry propagation bugs in the implementation of squaring for several raw math classes have been fixed (org.bouncycastle.math.raw.Nat???). These classes are used by our custom elliptic curve implementations (org.bouncycastle.math.ec.custom.**), so there was the possibility of rare (in general usage) spurious calculations for elliptic curve scalar multiplications. Such errors would have been detected with high probability by the output validation for our scalar multipliers." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2015-0225 (24 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0225 -r https://github.com/apache/cassandra -e c041ea8b3748089937168839791a6d64382b34de  -sie -u

echo "Importing CVE-2018-8032 (25 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8032 -r https://github.com/apache/axis1-java/ -e e7ce8a92bc02be54da102efb64c99aeee21a2106  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEAXIS-32456,http://mail-archives.apache.org/mod_mbox/axis-java-dev/201807.mbox/%3CJIRA.13170716.1531060536000.93536.1531060560060@Atlassian.JIRA%3E,https://issues.apache.org/jira/browse/AXIS-2924"  -sie -u

echo "Importing CVE-2019-1003005 (26 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003005 -r https://github.com/jenkinsci/script-security-plugin/ -e 35119273101af26792457ec177f34f6f4fa49d99  -descr "A sandbox bypass vulnerability exists in Jenkins Script Security Plugin 1.50 and earlier in src/main/java/org/jenkinsci/plugins/scriptsecurity/sandbox/groovy/SecureGroovyScript.java that allows attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003005,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1292"  -sie -u

echo "Importing CVE-2015-8320 (27 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-8320 -r https://github.com/apache/cordova-android -e 032ea8a8d386d8bcffc5de7fd3e4202478effb7d  -sie -u

echo "Importing CVE-2018-8025 (28 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8025 -r https://github.com/apache/hbase/ -e 30e98b4455f971c9cb3c02ac7b2daeebe4ee6f2:1.4,0c42acbdf86d08af3003105a26a2201f75f2e2c:master,7fe07075b35a816725ba18f6dd43d3fa84e08f9:2.0,bf25c1cb7221178388baaa58f0b16a408e151a6:1.3,625d4d002620139f49c8201f95b789b6a715cd4:1.2  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEHBASE-32391,https://issues.apache.org/jira/browse/HBASE-20664"  -sie -u

echo "Importing CVE-2013-6429 (29 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6429 -r https://github.com/spring-projects/spring-framework -e 2ae6a6a3415eebc57babcb9d3e5505887eda6d8:4_x,7387cb990e35b0f1b573faf29d4f9ae183d7a5e:3_2_x  -sie -u

echo "Importing CVE-2017-9787 (30 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9787 -r https://github.com/apache/struts -e 0d6442bab5b44d93c4c2e63c5335f0a331333b9:STRUTS_2_5_x,086b63735527d4bb0c1dd0d86a7c0374b825ff2:STRUTS_2_3_x  -descr "When using a Spring AOP functionality to secure Struts actions it is possible to perform a DoS attack when user was properly authenticated. Affected Software  Struts 2.3.7 - Struts 2.3.32, Struts 2.5 - Struts 2.5.10.1.  Upgrade to Apache Struts version 2.5.12 or 2.3.33." -links "http://struts.apache.org/docs/s2-049.html"  -sie -u

echo "Importing CVE-2010-0684 (31 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2010-0684 -r https://github.com/apache/activemq -e 9dc43f3ffe85c9c56faee235a21f23bfceb865c8,fed39c3619825bd92990cf1aa7a4e85119e00a6e,2895197d0dad246757d8d1d9eea181cbf0543ae9  -sie -u

echo "Importing CVE-2016-10006 (32 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-10006 -r https://github.com/nahsra/antisamy -e 7313931dc3c0d1377b010f07faef2063dd359a36  -sie -u

echo "Importing CVE-2017-1000242 (33 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000242 -r https://github.com/jenkinsci/git-client-plugin/ -e 75ea3fe05650fc6ca09046a72493e2b3f066fb98  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32198,https://jenkins.io/security/advisory/2017-04-27/"  -sie -u

echo "Importing CVE-2018-1002200 (34 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1002200 -r https://github.com/codehaus-plexus/plexus-archiver/ -e 58bc24e465c0842981692adbf6d75680298989de  -descr "A well crafted zip file may cause the code to extract outside of the destination directory. Description: Arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive, that holds path traversal filenames. When the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder. Fixed Version : 3.6.0" -links "https://snyk.io/research/zip-slip-vulnerability,https://github.com/codehaus-plexus/plexus-archiver/pull/87"  -sie -u

echo "Importing CVE-2015-0263 (35 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0263 -r https://github.com/apache/camel -e 7d19340bcdb42f7aae584d9c5003ac4f7ddaee36  -sie -u

echo "Importing CVE-2018-7489 (36 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-7489 -r https://github.com/FasterXML/jackson-databind -e e8f043d1aac9b82eee907e0f0c3abbdea723a935,60d459cedcf079c6106ae7da2ac562bc32dcabe1,6799f8f10cc78e9af6d443ed6982d00a13f2e7d2,ddfddfba6414adbecaff99684ef66eebd3a92e92  -links "https://github.com/FasterXML/jackson-databind/issues/1931,https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062"  -sie -u

echo "Importing CVE-2018-1306 (37 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1306 -r https://github.com/apache/portals-pluto/ -e 89f6a59a740d0a8318640ca6015e9a381c5c6b50  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEPORTALSPLUTO-32393,http://portals.apache.org/pluto/security.html"  -sie -u

echo "Importing CVE-2018-1000105 (38 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000105 -r https://github.com/jenkinsci/gerrit-trigger-plugin -e a222f2d9d1bca3422e6a462a7f587ae325455b80  -sie -u

echo "Importing CVE-2016-6814 (39 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6814 -r https://github.com/apache/groovy/ -e 4df8b652aa018a5d5d1cda8fba938bf3422db31c  -sie -u

echo "Importing HADOOP-14246 (40 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-14246 -r https://github.com/apache/hadoop/ -e 4dd6206547de8f694532579e37ba8103bafaeb1:3.x,f20aa38a1de73dd4a0b3a5b30636e8af246cd36:2.9,88d951e30bb34d9a6e1e2a181419a7fcc88ebfd:2.7  -descr "Authentication Tokens should use SecureRandom instead of Random and 256 bit secrets. Description: RandomSignerSecretProvider and ZKSignerSecretProvider currently use a long generated by Random (which is then converted to a String and is 160 bits) for secrets. We should improve this to use 256 bit secrets generated by SecureRandom. Fixed Version/s: 2.9.0, 3.0.0-alpha4, 2.8.4, 2.7.6" -links "https://issues.apache.org/jira/browse/HADOOP-14246,http://hadoop.apache.org/docs/r2.7.6/hadoop-project-dist/hadoop-common/releasenotes.html"  -sie -u

echo "Importing CVE-2018-17193 (41 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17193 -r https://github.com/apache/nifi/ -e e62aa0252dfcf34dff0c3a9c51265b1d0f9dfc9f  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHENIFI-72713,https://issues.apache.org/jira/browse/NIFI-5442,https://nifi.apache.org/security.html#CVE-2018-17193"  -sie -u

echo "Importing CVE-2018-1000149 (42 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000149 -r https://github.com/jenkinsci/ansible-plugin/ -e 06d30e5b626a978e258a7f4ab473cd7f53a7cba7  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32216,https://jenkins.io/security/advisory/2018-03-26/#SECURITY-630"  -sie -u

echo "Importing CVE-2013-6447 (43 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6447 -r https://github.com/seam2/jboss-seam -e 090aa6252affc978a96c388e3fc2c1c2688d9bb5  -sie -u

echo "Importing CVE-2017-8046 (44 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8046 -r https://github.com/spring-projects/spring-data-rest -e 8f269e28fe8038a6c60f31a1c36cfda04795ab45,824e51a1304bbc8334ac0b96ffaef588177e6cc:2.6.x  -descr "Malicious PATCH requests submitted to spring-data-rest servers can use specially crafted JSON data to run arbitrary Java code. Releases that have fixed this issue include: Spring Data REST 2.5.12, 2.6.7, 3.0 RC3, Spring Boot 2.0.0.M4,Spring Data release train Kay-RC3." -links "https://pivotal.io/security/cve-2017-8046"  -sie -u

echo "Importing CVE-2014-0113 (45 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0113 -r https://github.com/apache/struts -e 74e26830d2849a84729b33497f729e0f033dc147  -descr "Fix for ue CVE-2014-0094, CVE-2014-0112, CVE-2014-0113 and CVE-2014-0116" -links "https://github.com/apache/struts/pull/70"  -sie -u

echo "Importing CVE-2017-1000354 (46 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000354 -r https://github.com/jenkinsci/jenkins/ -e 02d24053bdfeb219d2387a19885a60bdab510479  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32181,https://jenkins.io/security/advisory/2017-04-26/"  -sie -u

echo "Importing CVE-2014-3490 (47 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3490 -r https://github.com/ronsigal/Resteasy -e 9b7d0f574cafdcf3bea5428f3145ab4908fc6d83  -sie -u

echo "Importing CVE-2018-1000863 (48 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000863 -r https://github.com/jenkinsci/jenkins/ -e 4ed66e5838476e575a83c3cd13fffb37eefa2f48  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-72671,https://jenkins.io/security/advisory/2018-12-05/#SECURITY-1072"  -sie -u

echo "Importing CVE-2018-1282 (49 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1282 -r https://github.com/apache/hive/ -e 0330c1c0b62f3c2e6a4744048578dea55193b62:2.6,63df42966cf44ffdd20d3fcdcfb70738c0432ab:2.3  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEHIVE-32204,https://issues.apache.org/jira/browse/HIVE-18788"  -sie -u

echo "Importing CVE-2018-8718 (50 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8718 -r https://github.com/jenkinsci/mailer-plugin -e 98e79cf904769907f83894e29f50ed6b3e7eb135  -links "http://www.openwall.com/lists/oss-security/2018/03/26/3"  -sie -u

echo "Importing CVE-2017-4995-JK (51 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4995-JK -r https://github.com/FasterXML/jackson-databind -e 60d459cedcf079c6106ae7da2ac562bc32dcabe1,6ce32ffd18facac6abdbbf559c817b47fcb622c:2.7.x  -descr "When configured to enable default typing, Jackson contained a deserialization vulnerability that could lead to arbitrary code execution. Jackson fixed this vulnerability by blacklisting known 'deserialization gadgets'. (see https://github.com/FasterXML/jackson-databind/issues/1599). Fixed in version 2.8.8.1, 2.7.9.1" -links "https://pivotal.io/security/cve-2017-4995"  -sie -u

echo "Importing CVE-2018-8026 (52 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8026 -r https://github.com/apache/lucene-solr/ -e e21d4937e0637c7b7949ac463f331da9a42c07f:master,3aa6086ed99fa7158d423dc7c33dae6da466b09:7.4,e5407c5a9710247e5f728aae36224a245a51f0b:7.x,d1baf6ba593561f39e2da0a71a8440797005b55:6.6.5,1880d4824e6c5f98170b9a00aad1d437ee2aa12:6.x  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESOLR-32408,https://issues.apache.org/jira/browse/SOLR-12450,https://mail-archives.apache.org/mod_mbox/lucene-solr-user/201807.mbox/%3C0cdc01d413b7%24f97ba580%24ec72f080%24%40apache.org%3E"  -sie -u

echo "Importing CVE-2018-1999044 (53 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999044 -r https://github.com/jenkinsci/jenkins -e e5046911c57e60a1d6d8aca9b21bd9093b0f3763  -sie -u

echo "Importing CVE-2017-3154 (54 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-3154 -r https://github.com/apache/atlas -e 0dcfd21bbfaac6f037f46b7aaaab0e5546fd2a7:0.7-incubating  -sie -u

echo "Importing CVE-2014-2058 (55 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2058 -r https://github.com/jenkinsci/jenkins -e b6b2a367a7976be80a799c6a49fa6c58d778b50e  -sie -u

echo "Importing CVE-2016-4433 (56 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4433 -r https://github.com/apache/struts -e b28b78c062f0bf3c79793a25aab8c9b6c12bce6e  -sie -u

echo "Importing ND4J-001 (57 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b ND4J-001 -r https://github.com/deeplearning4j/deeplearning4j/ -e f51f4242d67eed9c97a46051cc0c6c72d0830a27  -descr "Arbitrary File Write via Archive Extraction (Zip Slip)Overview: org.nd4j:nd4j-common is a Deeplearning4j, ND4J, DataVec and more - deep learning & linear algebra for Java/Scala with GPUs + Spark - From Skymind.Details: Affected versions of the package are vulnerable to Arbitrary File Write via Archive Extraction (AKA 'Zip Slip'). It is exploited using a specially crafted zip archive, that holds path traversal filenames. When exploited, a filename in a malicious archive is concatenated to the target extraction directory, which results in the final path ending up outside of the target folder. For instance, a zip may hold a file with a '../../file.exe' location and thus break out of the target folder. If an executable or a configuration file is overwritten with a file containing malicious code, the problem can turn into an arbitrary code execution issue quite easily.Remediation: A fix was pushed into the master branch but not yet published (2018-10-31)." -links "https://github.com/deeplearning4j/deeplearning4j/pull/6630,https://snyk.io/vuln/SNYK-JAVA-ORGND4J-72550"  -sie -u

echo "Importing CVE-2013-7398 (58 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7398 -r https://github.com/AsyncHttpClient/async-http-client -e 3c9152e2c75f7e8b654beec40383748a14c6b51b,a894583921c11c3b01f160ada36a8bb9d5158e9:1.9.x  -sie -u

echo "Importing CVE-2015-5348 (59 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5348 -r https://github.com/apache/camel -e 735ee02c693964b5f700af13a2adfeae56b848a4,e7fd5f049c2fd51a528f8062da91a1c75e33b0e8,349109b0834764560f0be69eb74f43a16bd220b0,c47cffcadabca0c588753555a386942184a33627,13e43c1412ad72d99030b4eb4cb72c84fa57d5ff,1b1ccbcd94860f6f1d8caf98fb59e6ab7b3940b4,a68434c258cdcd30587ae7adc5dabbac43eadbbf,92081b203523c5ed502ed41df43cbd8655caf9b9,c558f30a6d3820faa3d8c4ad5e54448914ec60d0,44e6a3036e5a11d90b60c142cf51ed74b792de31,190d7c81b7e3ce767514e319630b1bbaf27e6817,7e28d0af471ea992eb74807a4abd1626b88d678a,0afcf721ff209eb10a24c5e4b48ca9d6727ea99a,4f065fe07c1dcd7b451e6005a6dc8e96d77da43e,9cbd5867fe73ef07ecba6f16d64689632e3f2a16,23655fe0c15189ca41a6e99c31a3c38001a7cdb0,94330f99acb6f28155793b253de9956c3798f3bb,ec4a48d38e7335b40efcb14979fad8144eb00acf,5ea0a6f6c6a54f1cddf9691a99b0c237afc95348,d853853469292cd54fd9662c3605030ab5a9566b,515c822148d52de9e7cdf4f6b01f7b793f2f273f,f7f0b18f6924fe0b01f32a25ed1e38e29b1bf8e5,c703479f5880a099c38f2fd5e63c7d9f0567e5ff  -sie -u

echo "Importing CVE-2015-2080 (60 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-2080 -r https://github.com/eclipse/jetty.project -e 3e7b5f0fa918633ec24bd1bc23d6ee76d32c7729,4df5647f6dfdc5fa7abb812afe9290d60b17c098  -descr "The exception handling code in Eclipse Jetty before 9.2.9.v20150224 allows remote attackers to obtain sensitive information from process memory via illegal characters in an HTTP header, aka JetLeak. (see https://bugs.eclipse.org/bugs/show_bug.cgi?id=460642, https://github.com/eclipse/jetty.project/blob/jetty-9.2.x/advisories/2015-02-24-httpparser-error-buffer-bleed.md)" -links "https://nvd.nist.gov/vuln/detail/CVE-2015-2080"  -sie -u

echo "Importing CVE-2018-12541 (61 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12541 -r https://github.com/eclipse-vertx/vert.x/ -e 269a583330695d1418a4f5578f7169350b2e1332  -links "https://snyk.io/vuln/SNYK-JAVA-IOVERTX-72443,https://github.com/eclipse-vertx/vert.x/issues/2648,https://bugs.eclipse.org/bugs/show_bug.cgi?id=539170"  -sie -u

echo "Importing CVE-2018-1309 (62 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1309 -r https://github.com/apache/nifi/ -e 28067a29fd13cdf8e21b440fc65c6dd67872522f  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHENIFI-32306,https://nifi.apache.org/security.html#CVE-2018-1309,https://github.com/apache/nifi/pull/2466"  -sie -u

echo "Importing JETTY-1042 (63 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b JETTY-1042 -r https://github.com/eclipse/jetty.project -e 02dd1975ec61052cb9a17342c9bbec289257b701  -descr "Cookie leak between requests sharing a connection. Affects releases < = 6.1.18, < = 7.0.0.M4. Please update to 6.1.19, 7.0.0.Rc0." -links "https://github.com/eclipse/jetty.project/blob/jetty-9.4.x/jetty-documentation/src/main/asciidoc/reference/troubleshooting/security-reports.adoc"  -sie -u

echo "Importing CVE-2014-0094 (64 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0094 -r https://github.com/apache/struts -e 74e26830d2849a84729b33497f729e0f033dc147  -descr "Fix for ue CVE-2014-0094, CVE-2014-0112, CVE-2014-0113 and CVE-2014-0116" -links "https://github.com/apache/struts/pull/70"  -sie -u

echo "Importing CVE-2016-8738 (65 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-8738 -r https://github.com/apache/struts -e 554b9dddb0fbd1e581ef577dd62a7c22955ad0f6  -descr "If an application allows enter an URL in a form field and built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL." -links "https://cwiki.apache.org/confluence/display/WW/S2-044"  -sie -u

echo "Importing CVE-2016-4003 (66 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4003 -r https://github.com/apache/struts -e 72471d7075681bea52046645ad7aa34e9c53751e,a89bbe22cd2461748d595a89a254de888a415e6c,5421930b49822606792f36653b17d3d95ef106f9  -descr "Cross-site scripting (XSS) vulnerability in the URLDecoder function in JRE before 1.8, as used in Apache Struts 2.x before 2.3.28, when using a single byte page encoding, allows remote attackers to inject arbitrary web script or HTML via multi-byte characters in a url-encoded parameter. CVE-2016-4003" -links "http://struts.apache.org/docs/s2-028.html"  -sie -u

echo "Importing CVE-2018-17194 (67 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17194 -r https://github.com/apache/nifi/ -e 748cf745628dab20b7e71f12b5dcfe6ed0bbf134  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHENIF-72714,https://issues.apache.org/jira/browse/NIFI-5628,https://nifi.apache.org/security.html#CVE-2018-17194"  -sie -u

echo "Importing CVE-2012-4387 (68 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-4387 -r https://github.com/apache/struts -e 87935af56a27235e9399308ee1fcfb74f8edcefa  -sie -u

echo "Importing CVE-2018-11775 (69 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11775 -r https://github.com/apache/activemq/ -e bde7097fb8173cf871827df7811b3865679b963d  -links "http://activemq.apache.org/security-advisories.html"  -sie -u

echo "Importing CVE-2014-8125 (70 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-8125 -r https://github.com/droolsjbpm/drools -e c48464c3b246e6ef0d4cd0dbf67e83ccd532c6d3  -sie -u

echo "Importing CVE-2018-1000613 (71 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000613 -r https://github.com/bcgit/bc-java/ -e cd98322b171b15b3f88c5ec871175147893c31e6,4092ede58da51af9a21e4825fbad0d9a3ef5a223  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000613"  -sie -u

echo "Importing CVE-2015-5170 (72 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5170 -r https://github.com/cloudfoundry/uaa -e a54f3fb8225ef7d5021ca7d4fb52bef1e884568e  -descr "CSRF Attack on PWS. It is possible to log the user into another account instead of the account they intended to log into because of the lack of CSRF checks." -links "https://www.cloudfoundry.org/cve-2015-5170-5173/"  -sie -u

echo "Importing CVE-2018-1999027 (73 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999027 -r https://github.com/jenkinsci/saltstack-plugin/ -e 5306bcc438ff989e4b1999a0208fd6854979999b  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32448,https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1009"  -sie -u

echo "Importing CVE-2018-1002201 (74 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1002201 -r https://github.com/zeroturnaround/zt-zip/ -e 759b72f33bc8f4d69f84f09fcb7f010ad45d6fff  -descr "This is an arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive, that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder." -links "https://snyk.io/research/zip-slip-vulnerability"  -sie -u

echo "Importing CVE-2016-4970 (75 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4970 -r https://github.com/netty/netty -e 9e2c400f89c5badc39919f811179d3d42ac5257c,524156f164a910b8b0978d27a2c700a19cd8048:4.0  -sie -u

echo "Importing CVE-2014-2061 (76 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2061 -r https://github.com/jenkinsci/jenkins -e bf539198564a1108b7b71a973bf7de963a6213ef  -sie -u

echo "Importing CVE-2014-3578 (77 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3578 -r https://github.com/spring-projects/spring-framework -e 8e096aeef55287dc829484996c9330cf755891a1,c6503ebbf7c9e21ff022c58706dbac5417b2b5eb:3.2.x  -sie -u

echo "Importing CVE-2014-7809 (78 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-7809 -r https://github.com/apache/struts/ -e 1f301038a751bf16e525607c3db513db835b2999  -links "https://cwiki.apache.org/confluence/display/WW/S2-023"  -sie -u

echo "Importing CVE-2018-18628 (79 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-18628 -r https://github.com/pippo-java/pippo/ -e c6b26551a82d2dd32097fcb17c13c3b830916296  -links "https://snyk.io/vuln/SNYK-JAVA-ROPIPPO-72565,https://github.com/pippo-java/pippo/issues/458"  -sie -u

echo "Importing CVE-2017-9735 (80 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9735 -r https://github.com/eclipse/jetty.project -e f3751d70787fd8ab93932a51c60514c2eb37cb58,042f325f1cd6e7891d72c7e668f5947b5457dc02,2baa1abe4b1c380a30deacca1ed367466a1a62ea  -sie -u

echo "Importing CVE-2012-6612 (81 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-6612 -r https://github.com/apache/lucene-solr -e f230486ce6707762c1a6e81655d0fac52887906d  -sie -u

echo "Importing CVE-2014-2067 (82 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2067 -r https://github.com/jenkinsci/jenkins -e 5d57c855f3147bfc5e7fda9252317b428a700014  -sie -u

echo "Importing CVE-2017-12197 (83 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12197 -r https://github.com/letonez/libpam4j -e 84f32f4001fc6bdcc125ccc959081de022d18b6d  -sie -u

echo "Importing CVE-2018-14627 (84 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-14627 -r https://github.com/wildfly/wildfly/ -e 883115ea2168343e870745f538a80b1ddc360914  -links "https://snyk.io/vuln/SNYK-JAVA-ORGWILDFLY-72289,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14627,https://issues.jboss.org/browse/WFLY-9107,https://github.com/wildfly/wildfly/pull/10675"  -sie -u

echo "Importing CVE-2015-1831 (85 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1831 -r https://github.com/apache/struts -e d832747d647df343ed07a58b1b5e540a05a4d51b  -sie -u

echo "Importing CVE-2018-10936 (86 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-10936 -r https://github.com/pgjdbc/pgjdbc -e cdeeaca47dc3bc6f727c79a582c9e4123099526e  -sie -u

echo "Importing CVE-2016-1000344 (87 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000344 -r https://github.com/bcgit/bc-java -e 9385b0ebd277724b167fe1d1456e3c112112be1f  -descr "DHIES allows the use of unsafe ECB mode. This algorithm is now removed from the provider." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2018-8010 (88 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8010 -r https://github.com/apache/lucene-solr -e 4ba409e0ff3dc38aad88f7b7ad69a76325272b8:6.6.4,6c4e45e28494d4d4d04fb89852d18c86fa3d5f8:7.3.1,96f079b4b47eaadff65c7aaf0e5bafe68e30ec3:7.4,1b760114216fcdfae138a8b37f183a9293c4911:master,6d082d5743dee7e08a86b3f2ef03bc025112512:6.x  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESOLR-32298,https://issues.apache.org/jira/browse/SOLR-12316,https://exchange.xforce.ibmcloud.com/vulnerabilities/143557"  -sie -u

echo "Importing CVE-2018-20318 (89 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-20318 -r https://github.com/Wechat-Group/WxJava/ -e 6272639f02e397fed40828a2d0da66c30264bc0e  -links "https://snyk.io/vuln/SNYK-JAVA-COMGITHUBBINARYWANG-72732,https://github.com/Wechat-Group/WxJava/issues/889"  -sie -u

echo "Importing CVE-2017-4973 (90 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4973 -r https://github.com/cloudfoundry/uaa -e 24bc5ade80560cedb9300940d2b398163ab0dc6:2.7.4.x,24c270ce725df890727b2bd7d8a4f338a3a58b7:3.6.x,9d44cb0c7c25ccae95bfa1c2d59ce46200c643cb,5eb43757d5a3a2c9e7aae1ef3d0b9b7e2a38851e  -descr "A vulnerability has been identified with the groups endpoint in UAA allowing users to elevate their privileges." -links "https://cloudfoundry.org/cve-2017-4973/"  -sie -u

echo "Importing CVE-2015-5175 (91 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5175 -r https://github.com/apache/cxf-fediz -e f65c961ea31e3c1851daba8e7e49fc37bbf77b19,90c898335786211d253c0503453e2f8b93e0d3fe  -sie -u

echo "Importing CVE-2018-1000067 (92 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000067 -r https://github.com/jenkinsci/jenkins -e 2d16b459205730d85e51499c2457109b234ca9d9  -sie -u

echo "Importing CVE-2018-1313 (93 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1313 -r https://github.com/apache/derby/ -e 4da5b2db5f3a60c1fa8ef616d88a7efe28b0c9d:trunk,a2027c64e185a9ce46929f352e2db03371c1f95:10.14  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1313,https://markmail.org/message/akkappppxcdqrgxk"  -sie -u

echo "Importing CVE-2017-12612 (94 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12612 -r https://github.com/apache/spark/ -e 4cba3b5a350f4d477466fc73b32cbd653eee840:2.2.x,9952b53b57498852cba799b47f00238e52114c7c,f7cbf90a72a19476ea2d3d1ddc96c45a24b9f57:2.0.x,8efc6e986554ae66eab93cd64a9035d716adbab:2.3.x,772a9b969aa179150aa216e9efd950e512e9d0b4,0b25a7d93359e348e11b2e8698990a53436b3c5:2.1.x  -links "https://www.cvedetails.com/vulnerability-list/vendor_id-45/product_id-38954/Apache-Spark.html,http://seclists.org/oss-sec/2017/q3/419,https://issues.apache.org/jira/browse/SPARK-20922"  -sie -u

echo "Importing CVE-2018-1272 (95 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1272 -r https://github.com/spring-projects/spring-framework/ -e ab2410c754b67902f002bfcc0c3895bd7772d39:5.0.5,e02ff3a0da50744b0980d5d665fd242eedea767:4.3.x  -links "https://pivotal.io/security/cve-2018-1272,https://jira.spring.io/browse/SPR-16635"  -sie -u

echo "Importing CVE-2018-1284 (96 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1284 -r https://github.com/apache/hive/ -e b0a58d245875dc1b3ac58a7cf1a61d3b17805e96  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEHIVE-32203,https://issues.apache.org/jira/browse/HIVE-18879,https://lists.apache.org/thread.html/29184dbce4a37be2af36e539ecb479b1d27868f73ccfdff46c7174b4@%3Cdev.hive.apache.org%3E"  -sie -u

echo "Importing CVE-2016-0784 (97 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0784 -r https://github.com/apache/openmeetings/ -e 6e5b1828f7813eedab08a31a46018a86bf715775  -links "http://openmeetings.apache.org/security.html"  -sie -u

echo "Importing CVE-2013-1965 (98 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-1965 -r https://github.com/apache/struts -e 7e6f641ebb142663cbd1653dc49bed725edf7f56  -sie -u

echo "Importing CVE-2017-4991 (99 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4991 -r https://github.com/cloudfoundry/uaa -e 7db5e5846961e08295b1ef7af909f267eebe5da:2.7.4.x,eb3f86054489039e11eabd54a8ec9a46c22abfc:2.7.4.x,bbf6751bc0d87c4a3aaf21b54e26ce328ab998b:3.6.x  -descr "It is possible to perform a RCE attack with a malicious Content-Type value. If the Content-Type value isn't valid an exception is thrown which is then used to display an error message to a user." -links "https://www.cloudfoundry.org/cve-2017-4992/"  -sie -u

echo "Importing CVE-2016-8629 (100 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-8629 -r https://github.com/keycloak/keycloak -e a78cfa4b2ca979a1981fb371cfdf2c7212f7b6e2  -sie -u

echo "Importing CVE-2018-12536 (101 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12536 -r https://github.com/eclipse/jetty.project -e a51920d650d924cc2cea011995624b394437c6e:9.4.x,53e8bc2a636707e896fd106fbee3596823c2cdc:9.3.x  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSEJETTY-32392,https://bugs.eclipse.org/bugs/show_bug.cgi?id=535670,https://github.com/CVEProject/cvelist/pull/655,https://github.com/eclipse/jetty.project/issues/2560"  -sie -u

echo "Importing CVE-2016-0779 (102 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0779 -r https://github.com/apache/tomee -e 58cdbbef9c77ab2b44870f9d606593b49cde76d9  -descr "The EJBd protocol provided by TomEE can exploit the 0-day vulnerability. This issue only affects you if you rely on EJBd protocol (proprietary remote EJB protocol). This one one is not activated by default on the 7.x series but it was on the 1.x ones. TomEE was subject to this vulnerability until versions 1.7.3 and 7.0.0-M1." -links "http://tomee.apache.org/security/tomee.html"  -sie -u

echo "Importing CVE-2015-8031 (103 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-8031 -r https://git.eclipse.org/r/hudson/org.eclipse.hudson.core -e 6362c295e80a651dcb6c7e8647984d52a974786b  -descr "Prior to version 3.3.2 Hudson exhibits a flaw in it's XML API processing that can allow access to potentially sensitive information on the filesystem of the Hudson master server." -links "https://wiki.eclipse.org/Hudson-ci/alerts/CVE-2015-8031"  -sie -u

echo "Importing CVE-2016-6793 (104 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6793 -r https://github.com/apache/wicket -e 134686ef7185d3f96fec953136ab4847cd36b68:1_5_x  -sie -u

echo "Importing CVE-2018-1000614 (105 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000614 -r https://github.com/opennetworkinglab/onos/ -e d59f36ce062b31be67221f6b668abaeb54011d49  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000614,https://snyk.io/vuln/SNYK-JAVA-ORGONOSPROJECT-32420,http://gms.cl0udz.com/ONOS_Vul.pdf"  -sie -u

echo "Importing CVE-2018-1000106 (106 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000106 -r https://github.com/jenkinsci/gerrit-trigger-plugin -e a222f2d9d1bca3422e6a462a7f587ae325455b80  -sie -u

echo "Importing CVE-2018-6331 (107 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-6331 -r https://github.com/facebook/buck/ -e 8c5500981812564877bd122c0f8fab48d3528ddf  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-6331"  -sie -u

echo "Importing CVE-2011-4343 (108 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2011-4343 -r https://github.com/apache/myfaces -e f4e8981e4b17cc1ee9d3c79f6cd34f7bb2201f7:2.0.x,ed925077332275b5cd652410f438bb4893566fb8  -links "https://issues.apache.org/jira/browse/MYFACES-3405,https://github.com/javaserverfaces/mojarra/issues/2251"  -sie -u

echo "Importing CVE-2018-12036 (109 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12036 -r https://github.com/jeremylong/DependencyCheck/ -e c106ca919aa343b95cca0ffff0a0b5dc20b2baf7  -links "https://github.com/snyk/zip-slip-vulnerability"  -sie -u

echo "Importing CVE-2018-1320 (110 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1320 -r https://github.com/apache/thrift/ -e d973409661f820d80d72c0034d06a12348c8705e  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1320,https://lists.apache.org/thread.html/da5234b5e78f1c99190407f791dfe1bf6c58de8d30d15974a9669be3@%3Cuser.thrift.apache.org%3E,https://issues.apache.org/jira/browse/THRIFT-4506"  -sie -u

echo "Importing CVE-2015-2913 (111 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-2913 -r https://github.com/orientechnologies/orientdb -e 668ece96be210e742a4e2820a3085b215cf55104  -sie -u

echo "Importing CVE-2015-6644 (112 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-6644 -r https://github.com/bcgit/bc-java -e 9bc10bbaa9620d691c58e2b37f31f0d31ceea61f,2d80e6cc6f5b78e159dba3277414e3bfea511dea,25aca54734b861ef109ac4943c4a5f98c0c1b885,874bab94a5baf426545948116cabe6f4ae338c20  -sie -u

echo "Importing CVE-2017-5638 (113 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5638 -r https://github.com/apache/struts -e 352306493971e7d5a756d61780d57a76eb1f519a:support-2-3,6b8272ce47160036ed120a48345d9aa884477228  -descr "It is possible to perform a RCE attack with a malicious Content-Type value. If the Content-Type value isn't valid an exception is thrown which is then used to display an error message to a user. This CVE refers both to https://cwiki.apache.org/confluence/display/WW/S2-045 and https://cwiki.apache.org/confluence/display/WW/S2-046" -links "https://cwiki.apache.org/confluence/display/WW/S2-045"  -sie -u

echo "Importing CVE-2014-2065 (114 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2065 -r https://github.com/jenkinsci/jenkins -e a0b00508eeb74d7033dc4100eb382df4e8fa72e7  -sie -u

echo "Importing CVE-2018-11787 (115 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11787 -r https://github.com/apache/karaf -e 434e52502528e91e20d2f87cec7732f1e6e554c:4.0.9,cfa213ad680ded70b70bf0c648891a06386ef63:4.1.1  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKARAFWEBCONSOLE-72391,https://issues.apache.org/jira/browse/KARAF-4993,https://lists.apache.org/thread.html/d9ba4c3104ba32225646879a057b75b54430f349c246c85469037d3c@%3Cdev.karaf.apache.org%3E"  -sie -u

echo "Importing CVE-2018-17785 (116 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17785 -r https://github.com/blynkkk/blynk-server/ -e 806bc7847a687203a904d24feb1a0278de889e62  -links "https://snyk.io/vuln/SNYK-JAVA-CCBLYNK-72416,https://github.com/blynkkk/blynk-server/issues/1256"  -sie -u

echo "Importing CVE-2016-3087 (117 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3087 -r https://github.com/apache/struts -e 6bd694b7980494c12d49ca1bf39f12aec3e03e2f:2_5_x:2_5_x,98d2692e434fe7f4d445ade24fe2c9860de1c13f:2_3_x:2_3_x  -sie -u

echo "Importing CVE-2013-6430 (118 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6430 -r https://github.com/spring-projects/spring-framework -e 7a7df6637478607bef0277bf52a4e0a03e20a248  -descr "The JavaScriptUtils.javaScriptEscape() method did not escape all characters that are sensitive within either a JS single quoted string, JS double quoted string, or HTML script data context. In most cases this will result in an unexploitable parse error but in some cases it could result in an XSS vulnerability." -links "http://pivotal.io/security/cve-2013-6430"  -sie -u

echo "Importing CVE-2018-5382 (119 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-5382 -r https://github.com/bcgit/bc-java/ -e 81b00861cd5711e85fe8dce2a0e119f684120255  -links "https://snyk.io/vuln/SNYK-JAVA-ORGBOUNCYCASTLE-31659,https://www.kb.cert.org/vuls/id/306792"  -sie -u

echo "Importing CVE-2013-2248 (120 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2248 -r https://github.com/apache/struts -e 3cfe34fefedcf0fdcfcb061c0aea34a715b7de6:STRUTS_2_3_15_X,630e1ba065a8215c4e9ac03bfb09be9d655c2b6e  -sie -u

echo "Importing CVE-2018-11788 (121 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11788 -r https://github.com/apache/karaf/ -e 0c36c50bc158739c8fc8543122a6740c54adafc:4.2.2,1ffa6d1c4555cab9737d76b49142528b57cfdfc:4.1.7  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKARAFSPECS-72887,https://issues.apache.org/jira/browse/KARAF-5911?page=com.atlassian.jira.plugin.system.issuetabpanels%3Aall-tabpanel,http://karaf.apache.org/security/cve-2018-11788.txt"  -sie -u

echo "Importing CVE-2016-4437 (122 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4437 -r https://github.com/apache/shiro -e 64d9f8341e1aa7ef1a29744e16ea7c578ca5deee  -sie -u

echo "Importing CVE-2016-3081 (123 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3081 -r https://github.com/apache/struts -e f238cf4f1091be19fbcfd086b042c86a1bcaa7fc  -sie -u

echo "Importing CVE-2017-1000391 (124 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000391 -r https://github.com/jenkinsci/jenkins/ -e 566a8ddb885f0bef9bc848e60455c0aabbf0c1d3  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32191,https://jenkins.io/security/advisory/2017-11-08/"  -sie -u

echo "Importing CVE-2018-1325 (125 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1325 -r https://github.com/sebfz1/wicket-jquery-ui/ -e 4ade74d87389935dee5ba49b8cdd0abb075cc50:8.x,22e414d693e8ef679ac6da38107fbc118a63f00:6.x,2fec03dbe2f6e8808f4bdc6b3195dff3e44f520:7.10.2  -links "https://snyk.io/vuln/SNYK-JAVA-COMGOOGLECODEWICKETJQUERYUI-32229,https://markmail.org/message/6bxjyaolehhq7jrl"  -sie -u

echo "Importing CVE-2017-15717 (126 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-15717 -r https://github.com/apache/sling-org-apache-sling-xss -e ec6764d165abc4df8cffd8439761bb2228887db9  -sie -u

echo "Importing CVE-2014-3600 (127 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3600 -r https://github.com/apache/activemq -e b9696ac80bb496b52d05c3884f81b0746d9af9e2  -descr "It is possible for a consumer dequeuing XML message(s) to specify an XPath based selector thus causing the broker to evaluate the expression and attempt to match it against the messages in the queue while also performing an XML external entity resolution. Upgrade to Apache ActiveMQ 5.10.1 or 5.11.0 (see https://issues.apache.org/jira/browse/AMQ-5333)" -sie -u

echo "Importing CVE-2018-1321 (128 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1321 -r https://github.com/apache/syncope -e 717289bc10b6f3b204cb6d14881f530174c6235:master,726231fbf7b817bd2a9467171dcb1c0087c75bc:1.2.11,ad31479c1c543ac7d26b8c882aa14f6c00c1fd0:2.0.8  -links "http://syncope.apache.org/security.html#CVE-2018-1321:_Remote_code_execution_by_administrators_with_report_and_template_entitlements"  -sie -u

echo "Importing CVE-2016-5394 (129 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-5394 -r https://github.com/apache/sling -e 7d2365a248943071a44d8495655186e4f14ea294  -descr "In the XSS Protection API module before 1.0.12 in Apache Sling, the encoding done by the XSSAPI.encodeForJSString() method is not restrictive enough and for some input patterns allows script tags to pass through unencoded, leading to potential XSS vulnerabilities. (see https://issues.apache.org/jira/browse/SLING-5946)" -links "https://nvd.nist.gov/vuln/detail/CVE-2016-5394"  -sie -u

echo "Importing CVE-2014-2059 (130 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2059 -r https://github.com/jenkinsci/jenkins -e ad38d8480f20ce3cbf8fec3e2003bc83efda4f7d  -sie -u

echo "Importing CVE-2014-0002 (131 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0002 -r https://github.com/apache/camel -e 54b65c1d30848835f26bd138c0ba407bc1e560d:camel-2.12.x,2ec54fa0c13ae65bdcccff764af081a79fcc05f:camel-2.11.x,341d4e6cca71c53c90962d1c3d45fc9e05cc50c6  -descr "The XSLT component in Apache Camel before 2.11.4 and 2.12.x before 2.12.3 allows remote attackers to read arbitrary files and possibly have other unspecified impact via an XML document containing an external entity declaration in conjunction with an entity reference, related to an XML External Entity (XXE) issue. (see also https://issues.apache.org/jira/browse/CAMEL-7129)" -links "https://nvd.nist.gov/vuln/detail/CVE-2014-0002"  -sie -u

echo "Importing CVE-2017-7669 (132 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7669 -r https://github.com/apache/hadoop -e bbe3b0857d383c5e4dc4a7ade90a88a3e24338b:branch-2.8.1,0319e74c2512d47d47ab9df834f5b6455be7d968  -sie -u

echo "Importing CVE-2017-8028 (133 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8028 -r https://github.com/spring-projects/spring-ldap -e 08e8ae289bbd1b581986c7238604a147119c1336  -descr "When connected to some LDAP servers, when no additional attributes are bound, and when using LDAP BindAuthenticator with org.springframework.ldap.core.support.DefaultTlsDirContextAuthenticationStrategy as the authentication strategy, and setting userSearch, authentication is allowed with an arbitrary password when the username is correct. This occurs because some LDAP vendors require an explicit operation for the LDAP bind to take effect. Affectes Spring-LDAP versions 1.3.0 - 2.3.1. Upgrade to Spring-LDAP version 2.3.2.RELEASE+" -links "https://pivotal.io/security/cve-2017-8028,https://github.com/spring-projects/spring-ldap/issues/430"  -sie -u

echo "Importing CVE-2018-1000111 (134 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000111 -r https://github.com/jenkinsci/subversion-plugin -e 25f6afbb02a5863f363b0a2f664ac717ace743b4  -sie -u

echo "Importing CVE-2017-1000393 (135 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000393 -r https://github.com/jenkinsci/jenkins/ -e d7ea3f40efedd50541a57b943d5f7bbed046d091  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32189,https://jenkins.io/security/advisory/2017-10-11/"  -sie -u

echo "Importing CVE-2019-1003028 (136 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003028 -r https://github.com/jenkinsci/jms-messaging-plugin -e be87ad81c8b3aac6486ca787e3953c8fb6271997  -descr "org.jenkins-ci.plugins:jms-messaging provides the following functionality:- A build trigger to submit jenkins jobs upon receipt of a matching message.- A build and post-build step that may be used to submit a message to the topic upon the completion of a job.- A build step to wait for a specific message.Affected versions of this package are vulnerable to Cross-Site Request Forgery (CSRF) in SSLCertificateAuthenticationMethod.java,  UsernameAuthenticationMethod.java that allows attackers with Overall/Read permission to have Jenkins connect to a JMS endpoint.RemediationUpgrade org.jenkins-ci.plugins:jms-messaging to version 1.1.2 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-173718,https://jenkins.io/security/advisory/2019-02-19/#SECURITY-1033"  -sie -u

echo "Importing CVE-2018-20227 (137 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-20227 -r https://github.com/eclipse/rdf4j/ -e df15a4d7a8f2789c043b27c9eafe1b30316cfa79  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSERDF4J-72708,https://github.com/eclipse/rdf4j/issues/1210"  -sie -u

echo "Importing CVE-2016-8739 (138 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-8739 -r https://github.com/apache/cxf -e 9deb2d17:3.1.x:3.1.x,d9e2a6e7,8e4970d9:3.0.x:3.0.x  -descr "Atom entity provider of Apache CXF JAX-RS is vulnerable to XXE. This vulnerability affects all versions of Apache CXF prior to 3.0.12, 3.1.9. CXF 3.0.x users should upgrade to 3.0.12 or later as soon as possible. CXF 3.1.x users should upgrade to 3.1.9 or later as soon as possible." -links "http://cxf.apache.org/security-advisories.data/CVE-2016-8739.txt.asc"  -sie -u

echo "Importing CVE-2017-4971 (139 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4971 -r https://github.com/spring-projects/spring-webflow -e 57f2ccb66946943fbf3b3f2165eac1c8eb6b1523,ec3d54d2305e6b6bce12f770fec67fe63008d45:2.5.x  -descr "Applications that do not change the value of the MvcViewFactoryCreator useSpringBinding property which is disabled by default (i.e. set to “false”) can be vulnerable to malicious EL expressions in view states that process form submissions but do not have a sub-element to declare explicit data binding property mappings. (see https://jira.spring.io/browse/SWF-1700)" -links "https://pivotal.io/security/cve-2017-4971"  -sie -u

echo "Importing CVE-2015-5256 (140 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5256 -r https://github.com/apache/cordova-android -e af2969dec58ca89150b84b5d57edcf63d4ce1302  -sie -u

echo "Importing CVE-2016-0831 (141 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0831 -r https://android.googlesource.com/platform/frameworks/opt/telephony -e 79eecef63f3ea99688333c19e22813f54d4a31b1  -sie -u

echo "Importing CVE-2017-9096-2 (142 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9096-2 -r https://github.com/itext/itextpdf -e ad38371c396ac5ffbfb28056809e8ffaa5a18ccd  -descr "The XML parsers in iText before 5.5.12 and 7.x before 7.0.3 do not disable external entities, which might allow remote attackers to conduct XML external entity (XXE) attacks via a crafted PDF." -links "https://nvd.nist.gov/vuln/detail/CVE-2017-9096"  -sie -u

echo "Importing CVE-2016-0783 (143 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0783 -r https://github.com/apache/openmeetings/ -e 7eef674039acd587bc46c1c399d3bdf058f0919b  -links "http://openmeetings.apache.org/security.html"  -sie -u

echo "Importing CVE-2018-1308 (144 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1308 -r https://github.com/apache/lucene-solr -e dd3be31f7062dcb2f3b2d7f0e89df29e197dee6:6.3.3,02c693f3713add1b4891cbaa87127de3a55c10f:master,739a79338856599084617d44b6a1b424af059aa:7.3.0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESOLR-32208,https://issues.apache.org/jira/browse/SOLR-11971"  -sie -u

echo "Importing CVE-2018-1000531 (145 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000531 -r https://github.com/inversoft/prime-jwt/ -e abb0d479389a2509f939452a6767dc424bb5e6ba  -links "https://snyk.io/vuln/SNYK-JAVA-COMINVERSOFT-32386,https://github.com/inversoft/prime-jwt/issues/3"  -sie -u

echo "Importing CVE-2018-12544 (146 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12544 -r https://github.com/vert-x3/vertx-web/ -e d814d22ade14bafec47c4447a4ba9bff090f05e:3.5.1,ac8692c618d6180a9bc012a2ac8dbec821b1a97:3.5.3  -links "https://snyk.io/vuln/SNYK-JAVA-IOVERTX-72440,https://github.com/vert-x3/vertx-web/issues/1021,https://bugs.eclipse.org/bugs/show_bug.cgi?id=539568"  -sie -u

echo "Importing CVE-2013-2134 (147 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2134 -r https://github.com/apache/struts -e 54e5c912ebd9a1599bfcf7a719da17c28127bbe:STRUTS_2_3_14_3,711cf0201cdd319a38cf29238913312355db29ba,cfb6e9afbae320a4dd5bdd655154ab9fe5a92c1:STRUTS_2_3_14_3,01e6b251b4db78bfb7971033652e81d1af4cb3e:STRUTS_2_3_14_3,8b4fc81daeea3834bcbf73de5f48d0021917aa3:STRUTS_2_3_14_3  -sie -u

echo "Importing CVE-2018-10862 (148 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-10862 -r https://github.com/wildfly/wildfly-core/ -e 40996ae6d5d3b6c1602a15f96b86a8d8a39b53eb  -links "https://snyk.io/vuln/SNYK-JAVA-ORGWILDFLYCORE-32441"  -sie -u

echo "Importing CVE-2016-1000346 (149 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000346 -r https://github.com/bcgit/bc-java -e 1127131c89021612c6eefa26dbe5714c194e7495  -descr "Other party DH public key not fully validated. This can cause issues as invalid keys can be used to reveal details about the other party's private key where static Diffie-Hellman is in use. As of this release the key parameters are checked on agreement calculation." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2016-1000341 (150 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000341 -r https://github.com/bcgit/bc-java -e acaac81f96fec91ab45bd0412beaf9c3acd8defa  -descr "DSA signature generation vulnerable to timing attack. Where timings can be closely observed for the generation of signatures, the lack of blinding in 1.55 or earlier, may allow an attacker to gain information about the signatures k value and ultimately the private value as well." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2014-0110 (151 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0110 -r https://github.com/apache/cxf -e 8f4799b5bc5ed0fe62d6e018c45d960e3652373e  -sie -u

echo "Importing CVE-2014-0112 (152 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0112 -r https://github.com/apache/struts -e 74e26830d2849a84729b33497f729e0f033dc147  -descr "Fix for ue CVE-2014-0094, CVE-2014-0112, CVE-2014-0113 and CVE-2014-0116" -links "https://github.com/apache/struts/pull/70"  -sie -u

echo "Importing CVE-2013-6407 (153 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6407 -r https://github.com/apache/lucene-solr -e f230486ce6707762c1a6e81655d0fac52887906d  -sie -u

echo "Importing CVE-2018-1000089 (154 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000089 -r https://github.com/jenkinsci/pipeline-build-step-plugin/ -e 3dfefdec1f7b2a4ee0ef8902afdea720b1572cb3  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32153,https://jenkins.io/security/advisory/2017-07-10/"  -sie -u

echo "Importing CVE-2018-1999042 (155 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999042 -r https://github.com/jenkinsci/jenkins -e 727d58f690abf64f543407e1de3545eca76ad30e  -sie -u

echo "Importing CVE-2018-1000861 (156 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000861 -r https://github.com/jenkinsci/jenkins/ -e 47f38d714c99e1841fb737ad1005618eb26ed852  -descr "" -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000861,https://jenkins.io/security/advisory/2018-12-05/#SECURITY-595,https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-72669"  -sie -u

echo "Importing CVE-2018-1305 (157 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1305 -r https://github.com/apache/tomcat/ -e 4d637bc3986e5d09b9363e2144b8ba74fa6eac3a,3e54b2a6314eda11617ff7a7b899c251e222b1a1  -links "https://tomcat.apache.org/security-7.html,https://tomcat.apache.org/security-8.html,https://tomcat.apache.org/security-9.html"  -sie -u

echo "Importing PRIMEFACES-1194 (158 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b PRIMEFACES-1194 -r https://github.com/primefaces/primefaces -e afcec249b82cad60978e8ecb3926822d3f51b25a,e8c0baae853c48bb1fb2d39833c5b2b6af837616  -descr "org.primefaces:primefaces is an UI library in Java EE Ecosystem. Affected versions of [org.primefaces:primefaces] are vulnerable to Cross-site Scripting (XSS). Remediation: Upgrade org.primefaces:primefaces to version 6.2 or higher." -links "https://github.com/primefaces/primefaces/issues/1194"  -sie -u

echo "Importing CVE-2018-11041 (159 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11041 -r https://github.com/cloudfoundry/uaa/ -e d17b23fc3bf9b86f111774925afadfced75315c:4.7.x,7d750e036cd52c5d30e73e28cbcae23126d7154:4.10.x,7a8f157f7e2feed2d0ebb63b163ff735b6340b9:4.19.0,57a15dfb7e0e3a59019ebe951793b586512b196:4.7.x,8a599448781acd481aa9dab1b0bde3424e00ced:4.10.x,f6362a8f1865314aa507fc5de772848b7e55236:4.19.0  -descr "UAA open redirect Severity. \nDescription: Cloud Foundry UAA, versions later than 4.6.0 and prior to 4.19.0 except 4.10.1 and 4.7.5 and uaa-release versions later than v48 and prior to v60 except v55.1 and v52.9, does not validate redirect URL values on a form parameter used for internal UAA redirects on the login page, allowing open redirects. A remote attacker can craft a malicious link that, when clicked, will redirect users to arbitrary websites after a successful login attempt.\nAffected Cloud Foundry Products and Versions:\nYou are using uaa versions later than 4.6.0 and prior to 4.19.0, except 4.10.1 and 4.7.5\nYou are using uaa-release versions later than v48 and prior to v60, except v55.1 and v52.9\nMitigation:\nReleases that have fixed this issue include\n- uaa versions 4.19.0, 4.10.1, 4.7.5\n- uaa-release versions v60, v55.1, v52.9\n" -links "https://www.cloudfoundry.org/blog/cve-2018-11041/"  -sie -u

echo "Importing CVE-2018-1999020 (160 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999020 -r https://github.com/opennetworkinglab/onos/ -e 4b19da6ce94de4865a365c200d6e8169ffb2184f  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1999020"  -sie -u

echo "Importing CVE-2016-8744 (161 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-8744 -r https://github.com/apache/brooklyn-server -e 3ae4a4d156341a53e54a2fe07192f46b15763d06  -sie -u

echo "Importing CVE-2018-19413 (162 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-19413 -r https://github.com/SonarSource/sonarqube/ -e 7b567ba3d15ed7dd0b0bba0330686487e35af85c  -links "https://snyk.io/vuln/SNYK-JAVA-ORGSONARSOURCESONARQUBE-72697,https://jira.sonarsource.com/browse/SONAR-11305"  -sie -u

echo "Importing CVE-2016-0731 (163 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0731 -r https://github.com/apache/ambari -e eaf8cc4cd2015456307ff3fcf98e49f2826fa270  -sie -u

echo "Importing CVE-2018-14371 (164 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-14371 -r https://github.com/eclipse-ee4j/mojarra/ -e 1b434748d9239f42eae8aa7d37d7a0930c061e24  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-14371,https://github.com/javaserverfaces/mojarra/issues/4364"  -sie -u

echo "Importing CVE-2014-0003 (165 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0003 -r https://github.com/apache/camel -e e922f89290f236f3107039de61af0375826bd96d,483b445dc77487e2d0f3d8c8bf1a7bbab04464c:camel-2.12.x,c6de749e9b3c7b61861c5480e91550290585224:camel-2.11.x  -descr "The XSLT component in Apache Camel 2.11.x before 2.11.4, 2.12.x before 2.12.3, and possibly earlier versions allows remote attackers to execute arbitrary Java methods via a crafted message. (see https://issues.apache.org/jira/browse/CAMEL-7123)" -links "https://nvd.nist.gov/vuln/detail/CVE-2014-0003"  -sie -u

echo "Importing CVE-2010-1632 (166 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2010-1632 -r https://github.com/apache/axis2-java -e 026d9037c3040580c2b04d8d8e4691c33a933418,dbb2a3d37baf651f34b3bb064badb0e2c377f46b  -sie -u

echo "Importing CVE-2014-3682 (167 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3682 -r https://github.com/kiegroup/jbpm-designer -e e4691214a100718c3b1c9b93d4db466672ba0be:6.2.x,69d8f6b7a099594bd0536f88d52875387585708:6.2.x,be3968d51299f6de0011324be60223ede49ecb1:6.0.x,5641588c730cc75dc3b76c34b76271fbd407fb8:6.0.x  -sie -u

echo "Importing CVE-2014-2062 (168 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2062 -r https://github.com/jenkinsci/jenkins -e 5548b5220cfd496831b5721124189ff18fbb12a3  -sie -u

echo "Importing CVE-2018-12585 (169 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12585 -r https://github.com/OPCFoundation/UA-Java/ -e 83fe7a9f9a510f35e3903bef907d22889f99b08b  -links "https://snyk.io/vuln/SNYK-JAVA-ORGOPCFOUNDATIONUA-72369,https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-12585,https://opcfoundation-onlineapplications.org/faq/SecurityBulletins/OPC_Foundation_Security_Bulletin_CVE-2018-12585.pdf"  -sie -u

echo "Importing CVE-2018-11039 (170 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11039 -r https://github.com/spring-projects/spring-framework/ -e f2694a8ed93f1f63f87ce45d0bb638478b426acd,dac97f1b7dac3e70ff603fb6fc9f205b95dd6b01  -descr "Cross Site Tracing (XST) with Spring Framework. Description: Spring Framework (versions 5.0.x prior to 5.0.7, versions 4.3.x prior to 4.3.18, and older unsupported versions) allow web applications to change the HTTP request method to any HTTP method (including TRACE) using the HiddenHttpMethodFilter in Spring MVC. If an application has a pre-existing XSS vulnerability, a malicious user (or attacker) can use this filter to escalate to an XST (Cross Site Tracing) attack. Affected Pivotal Products and Versions: Spring Framework 5.0 to 5.0.6, Spring Framework 4.3 to 4.3.17, Older unsupported versions are also affected. Mitigation: Users of affected versions should apply the following mitigation: \n- 5.0.x users should upgrade to 5.0.7. \n- 4.3.x users should upgrade to 4.3.18. \n- Older versions should upgrade to a supported branch. \nThere are no other mitigation steps necessary. This attack applies to applications that: \n1/ Use the HiddenHttpMethodFilter (it is enabled by default in Spring Boot). \n2/ Allow HTTP TRACE requests to be handled by the application server. \nThis attack is not exploitable directly because an attacker would have to make a cross-domain request via HTTP POST, which is forbidden by the Same Origin Policy. This is why a pre-existing XSS (Cross Site Scripting) vulnerability in the web application itself is necessary to enable an escalation to XST." -links "https://jira.spring.io/browse/SPR-16836,https://pivotal.io/security/cve-2018-11039"  -sie -u

echo "Importing CVE-2018-8017 (171 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8017 -r https://github.com/apache/tika/ -e 8a6a9e1344f5b10ebfa1a189dc3c30d0da2b9d4:1.x,62926cae31a02d4f23d21148435804b96c543cc:1.19  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHETIKA-72394,https://lists.apache.org/thread.html/72df7a3f0dda49a912143a1404b489837a11f374dfd1961061873a91@%3Cdev.tika.apache.org%3E"  -sie -u

echo "Importing CVE-2016-1000339 (172 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000339 -r https://github.com/bcgit/bc-java -e 413b42f4d770456508585c830cfcde95f9b0e93b  -descr "AESFastEngine has a side channel leak if table accesses can be observed. The use of lookup large static lookup tables in AESFastEngine means that where data accesses by the CPU can be observed, it is possible to gain information about the key used to initialize the cipher. We now recommend not using AESFastEngine where this might be a concern. The BC provider is now using AESEngine by default." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2018-1067 (173 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1067 -r https://github.com/undertow-io/undertow/ -e 85d4478e598105fe94ac152d3e11e388374e8b8:1.4,f404cb68448c188f4d51b085b7fe4ac32bde26e:2.0.7  -links "https://snyk.io/vuln/SNYK-JAVA-IOUNDERTOW-32300"  -sie -u

echo "Importing CVE-2014-1904 (174 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-1904 -r https://github.com/spring-projects/spring-framework -e 75e08695a04980dbceae6789364717e9d8764d58,741b4b229ae032bd17175b46f98673ce0bd2d485  -sie -u

echo "Importing APACHE-COMMONS-001 (175 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b APACHE-COMMONS-001 -r https://github.com/apache/commons-compress/ -e a080293da69f3fe3d11d5214432e1469ee195870  -descr "Overview: org.apache.commons:commons-compress defines an API for working with compression and archive formats. Affected versions of this package are vulnerable to Directory Traversal.\n Remediation: Upgrade org.apache.commons:commons-compress to version 1.18-RC1 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHECOMMONS-72275,https://github.com/apache/commons-compress/commit/a080293da69f3fe3d11d5214432e1469ee195870"  -sie -u

echo "Importing CVE-2013-4330 (176 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4330 -r https://github.com/apache/camel -e ce19353f1297c5d3dc59be21a1ead89c0a44907:camel-2.11.x,5ba8f63f78f82b0cddf6cecbf59ac444a0cae2a6,27a9752a565fbef436bac4fcf22d339e3295b2a:camel-2.9.x,3215fe50dd42c83a7a454dd36486843fe36eae4:camel-2.10.x,2281b1f365c50ee1a470fb9990b753eadee9095:camel-2.12.x  -sie -u

echo "Importing CVE-2018-17195 (177 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17195 -r https://github.com/apache/nifi/ -e 246c090526143943557b15868db6e8fe3fb30cf6  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHENIFI-72715,https://issues.apache.org/jira/browse/NIFI-5595,https://nifi.apache.org/security.html#CVE-2018-17195"  -sie -u

echo "Importing CVE-2019-1003012 (178 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003012 -r https://github.com/jenkinsci/blueocean-plugin/ -e 1a03020b5a50c1e3f47d4b0902ec7fc78d3c86ce  -descr "A data modification vulnerability exists in Jenkins Blue Ocean Plugins 1.10.1 and earlier in blueocean-core-js/src/js/bundleStartup.js, blueocean-core-js/src/js/fetch.ts, blueocean-core-js/src/js/i18n/i18n.js, blueocean-core-js/src/js/urlconfig.js, blueocean-rest/src/main/java/io/jenkins/blueocean/rest/APICrumbExclusion.java, blueocean-web/src/main/java/io/jenkins/blueocean/BlueOceanUI.java, blueocean-web/src/main/resources/io/jenkins/blueocean/BlueOceanUI/index.jelly that allows attackers to bypass all cross-site request forgery protection in Blue Ocean API." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003012,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1201"  -sie -u

echo "Importing CVE-2016-5016 (179 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-5016 -r https://github.com/cloudfoundry/uaa -e 90b6f8c06afd96efd39f87deaaf9a94cd0fd082:2.7.4.x,bc91ccd2029e8f1cea0c647f0c9aad4585f7a2c:3.3.0.x,0a78612f981c541ad2d997e6a365f2a0b3e799d9  -descr "UAA uses the OpenJDK Java Runtime Environment TrustManager to store trusted certificates. TrustManager does not by default check certificates for expiration. UAA was found to accept expired certificates." -links "https://www.cloudfoundry.org/cve-2016-5016-uaa-accepts-expired-certificates/"  -sie -u

echo "Importing CVE-2013-6408 (180 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6408 -r https://github.com/apache/lucene-solr -e 7239a57a51ea0f4d05dd330ce5e15e4f72f72747  -sie -u

echo "Importing CVE-2015-1836 (181 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1836 -r https://github.com/apache/hbase -e 942e09b71eef5bd9fdb1c8711125c4bc1193bcdc  -sie -u

echo "Importing CVE-2017-12159 (182 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12159 -r https://github.com/keycloak/keycloak -e 9b75b603e3a5f5ba6deff13cbb45b070bf2d2239  -sie -u

echo "Importing CVE-2015-5204 (183 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5204 -r https://github.com/apache/cordova-plugin-file-transfer -e 2b31723708256c08c5209308eb6ccfb03e2ab990,ad6647120db12f0e67ee4a952a71ea494a39a475,8fcdb1aa3deb892691b44bdf57e8d780da09e2a4  -sie -u

echo "Importing CVE-2018-12418 (184 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12418 -r https://github.com/junrar/junrar/ -e ad8d0ba8e155630da8a1215cee3f253e0af45817  -links "https://snyk.io/vuln/SNYK-JAVA-COMGITHUBJUNRAR-32372,https://github.com/junrar/junrar/pull/8"  -sie -u

echo "Importing CVE-2017-2670 (185 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-2670 -r https://github.com/undertow-io/undertow/ -e 9bfe9fbbb595d51157b61693f072895f7dbadd1d  -links "https://snyk.io/vuln/SNYK-JAVA-IOUNDERTOW-32442,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2670"  -sie -u

echo "Importing HADOOP-13105 (186 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-13105 -r https://github.com/apache/hadoop/ -e e54f073cfe485842b57d0a52330b59df0b38cb2:2.8,5e6ee5aafb9b9f200d906444e4731cfc60ac6eb:2.9,d82bc8501869be78780fc09752dbf7af918c14a:3.x  -descr "LdapGroupsMapping currently does not set timeouts on the LDAP queries. This can create a risk of a very long/infinite wait on a connection. This patch adds two new config keys for supporting timeouts in LDAP query operations. The property hadoop.security.group.mapping.ldap.connection.timeout.ms is the connection timeout (in milliseconds), within which period if the LDAP provider doesn't establish a connection, it will abort the connect attempt. The property hadoop.security.group.mapping.ldap.read.timeout.ms is the read timeout (in milliseconds), within which period if the LDAP provider doesn't get a LDAP response, it will abort the read attempt. Fixed Version/s: 2.8.0, 3.0.0-alpha1, 2.7.6." -links "https://issues.apache.org/jira/browse/HADOOP-13105,http://hadoop.apache.org/docs/r2.7.6/hadoop-project-dist/hadoop-common/releasenotes.html"  -sie -u

echo "Importing CVE-2018-6356 (187 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-6356 -r https://github.com/jenkinsci/jenkins -e eb03a42078f29dbed3742b8740c95e02890e4545,9de62915807deab61d6e780eed660428f9889b51  -sie -u

echo "Importing CVE-2015-5254 (188 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5254 -r https://github.com/apache/activemq -e a7e2a44fe8d4435ae99532eb0ab852e6247f7b16,6f03921b31d9fefeddb0f4fa63150ed1f94a14b:activemq-5.11.x,e7a4b53f799685e337972dd36ba0253c04bcc01:activemq-5.12.x,d7a3b9406b8496c3f1508bebf3c7ff5367374b90,e100638244c4ca5eb2a1f16bcdc671c9859c2694,73a0caf758f9e4916783a205c7e422b4db27905:activemq-5.11.x,7eb9b218b2705cf9273e30ee2da026e43b6dd4e:activemq-5.12.x  -sie -u

echo "Importing CVE-2018-1257 (189 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1257 -r https://github.com/spring-projects/spring-framework/ -e 246a6db1cad205ca9b6fca00c544ab7443ba202:4.3.x,ff2228fdaf131d57b5c8c5918ee8d07c6dd9bba:5.0.x  -links "https://pivotal.io/security/cve-2018-1257,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORK-31674"  -sie -u

echo "Importing CVE-2018-8036 (190 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8036 -r https://github.com/apache/pdfbox/ -e 038c09b5f361e083a00ce076c95521b73202fcb4  -descr "In Apache PDFBox 1.8.0 to 1.8.14 and 2.0.0RC1 to 2.0.10, a carefully crafted (or fuzzed) file can trigger an infinite loop which leads to an out of memory exception in Apache PDFBox's AFMParser." -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEPDFBOX-32417,https://lists.apache.org/thread.html/9f62f742fd4fcd81654a9533b8a71349b064250840592bcd502dcfb6@%3Cusers.pdfbox.apache.org%3E,https://svn.apache.org/viewvc?view=revision&revision=1834048"  -sie -u

echo "Importing CVE-2009-3555-JETTY (191 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2009-3555-JETTY -r https://github.com/eclipse/jetty.project -e 102625b86c8e82e0e3d02a71028ba62795aff52b,b4390f98529fce165e6394b94122b427fdfb8a5e,b90ad09443e1771e37d23e393afe842759c20454  -descr "Work  around by turning off SSL renegotiation in Jetty. If using JVM > 1.6u19 setAllowRenegotiate(true) may be called on connectors. This vulnerability affects JVM<1.6u19. Please upgrade to jetty-7.01.v20091125, jetty-6.1.22 (see http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2009-3555 and http://www.kb.cert.org/vuls/id/120541)" -links "https://github.com/eclipse/jetty.project/blob/jetty-9.4.x/jetty-documentation/src/main/asciidoc/reference/troubleshooting/security-reports.adoc"  -sie -u

echo "Importing CVE-2019-1003006 (192 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003006 -r https://github.com/jenkinsci/groovy-plugin/ -e 212e048a319ae32dad4cfec5e73a885a9f4781f0  -descr "A sandbox bypass vulnerability exists in Jenkins Groovy Plugin 2.0 and earlier in src/main/java/hudson/plugins/groovy/StringScriptSource.java that allows attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003006,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1293"  -sie -u

echo "Importing CVE-2016-3720 (193 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3720 -r https://github.com/FasterXML/jackson-dataformat-xml -e f0f19a4c924d9db9a1e2830434061c8640092cc0  -sie -u

echo "Importing CVE-2018-1000130 (194 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000130 -r https://github.com/rhuss/jolokia -e fd7b93da30c61a45bac10d8b311f1b79a74910f:master,1b360b8889f0ed51165a8d1ac55dd8e0aa2dfd4:master  -sie -u

echo "Importing CVE-2019-1003024 (195 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003024 -r https://github.com/jenkinsci/script-security-plugin/ -e 3228c88e84f0b2f24845b6466cae35617e082059  -descr "org.jenkins-ci.plugins:script-security allows Jenkins administrators to control what in-process scripts can be run by less-privileged users.Affected versions of this package are vulnerable to Arbitrary Code Execution in RejectASTTransformsCustomizer.java. It is possible for attackers with Overall/Read permission to provide a Groovy script to an HTTP endpoint that can result in arbitrary code execution on the Jenkins master JVM.RemediationUpgrade org.jenkins-ci.plugins:script-security to version 1.5.3 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-173716,https://jenkins.io/security/advisory/2019-02-19/#SECURITY-1320"  -sie -u

echo "Importing CVE-2018-1259 (196 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1259 -r https://github.com/SvenEwald/xmlbeam/ -e f8e943f44961c14cf1316deb56280f7878702ee1  -links "https://pivotal.io/security/cve-2018-1259,https://snyk.io/vuln/SNYK-JAVA-ORGXMLBEAM-31677"  -sie -u

echo "Importing CVE-2018-11040 (197 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11040 -r https://github.com/spring-projects/spring-framework/ -e b80c13b722bb207ddf43f53a007ee3ddc1dd2e2:5.0.x,874859493bbda59739c38c7e52eb3625f247b93:4.3.x  -descr "JSONP enabled by default in MappingJackson2JsonView. Description: Spring Framework, versions 5.0.x prior to 5.0.7, versions 4.3.x prior to 4.3.18, and older unsupported versions, allows web applications to enable cross-domain requests via JSONP (JSON with Padding) through AbstractJsonpResponseBodyAdvice for REST controllers, and MappingJackson2JsonView for browser requests. Both are not enabled by default in Spring Framework nor Spring Boot. However when MappingJackson2JsonView is configured in an application, JSONP support is automatically ready to use through the jsonp and callback JSONP parameters, enabling cross-domain requests.\nAllowing cross-domain requests from untrusted origins may expose user information to 3rd party browser scripts.\nThis vulnerability applies to applications that:\n - Explicitly configure MappingJackson2JsonView.\n - And do not set the jsonpParameterNames property of MappingJackson2JsonView to an empty set.\n - And expose sensitive user information over endpoints that can render content with JSONP.\n\nAffected Pivotal Products and Versions: Spring Framework 5.0 to 5.0.6. pring Framework 4.1 to 4.3.17. Mitigation: Users of affected versions should apply the following mitigation:\n- 5.0.x users should upgrade to 5.0.7.\n- 4.3.x users should upgrade to 4.3.18.\n- Older versions should upgrade to a supported branch, or otherwise set MappingJacksonJsonViews jsonpParameterNames property to an empty set.\n\nApplications that do require JSONP support will need to explicitly configure the jsonpParameterNames property of MappingJacksonJsonView following the upgrade. It is recommended that applications switch to using CORS instead of JSONP to enable cross-domain requests. JSONP support in the Spring Framework is deprecated as of 5.0.7 and 4.3.18 and will be removed in 5.1." -links "https://pivotal.io/security/cve-2018-11040,https://jira.spring.io/browse/SPR-16798"  -sie -u

echo "Importing CVE-2018-11761 (198 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11761 -r https://github.com/apache/tika/ -e 4e67928412ad56333d400f3728ecdb59d07d9d63  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHETIKA-72400,https://lists.apache.org/thread.html/5553e10bba5604117967466618f219c0cae710075819c70cfb3fb421@%3Cdev.tika.apache.org%3E"  -sie -u

echo "Importing CVE-2018-8015 (199 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8015 -r https://github.com/apache/orc/ -e d5018d309a8adc6b8e0567cb692a17371d16e108  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-8015,https://orc.apache.org/security/CVE-2018-8015/,https://github.com/apache/orc/pull/266"  -sie -u

echo "Importing CVE-2015-8581 (200 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-8581 -r https://github.com/apache/tomee -e 58cdbbef9c77ab2b44870f9d606593b49cde76d9  -sie -u

echo "Importing CVE-2016-1000345 (201 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000345 -r https://github.com/bcgit/bc-java/ -e 21dcb3d9744c83dcf2ff8fcee06dbca7bfa4ef35  -links "https://snyk.io/vuln/SNYK-JAVA-ORGBOUNCYCASTLE-32367"  -sie -u

echo "Importing CVE-2015-3192 (202 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-3192 -r https://github.com/spring-projects/spring-framework -e 5a711c05ec750f069235597173084c2ee796242:3.2.x  -sie -u

echo "Importing CVE-2014-2066 (203 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2066 -r https://github.com/jenkinsci/jenkins -e 8ac74c350779921598f9d5edfed39dd35de8842a  -sie -u

echo "Importing CVE-2016-9878 (204 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-9878 -r https://github.com/spring-projects/spring-framework -e e2d6e709c3c65a4951eb096843ee75d5200cfcad:4.3.x,43bf008fbcd0d7945e2fcd5e30039bc4d74c7a98:4.2.x,a7dc48534ea501525f11369d369178a60c2f47d0:3.2.x  -sie -u

echo "Importing CVE-2016-6809 (205 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6809 -r https://github.com/apache/tika -e 8a68b5d474205cc91cbbb610d4a1c05af57f0610  -sie -u

echo "Importing CVE-2016-4438 (206 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4438 -r https://github.com/apache/struts -e 76eb8f38a33ad0f1f48464ee1311559c8d52dd6d  -sie -u

echo "Importing CVE-2019-1003016 (207 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003016 -r https://github.com/jenkinsci/job-import-plugin/ -e 1d81e59330d371d15d3672dabc17d35dcd9fb824  -descr "An exposure of sensitive information vulnerability exists in Jenkins Job Import Plugin 2.1 and earlier in src/main/java/org/jenkins/ci/plugins/jobimport/JobImportAction.java, src/main/java/org/jenkins/ci/plugins/jobimport/JobImportGlobalConfig.java, src/main/java/org/jenkins/ci/plugins/jobimport/model/JenkinsSite.java that allows attackers with Overall/Read permission to have Jenkins connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003016,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-905%20(2)"  -sie -u

echo "Importing CVE-2019-1003015 (208 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003015 -r https://github.com/jenkinsci/job-import-plugin/ -e 1d81e59330d371d15d3672dabc17d35dcd9fb824  -descr "An XML external entity processing vulnerability exists in Jenkins Job Import Plugin 2.1 and earlier in src/main/java/org/jenkins/ci/plugins/jobimport/client/RestApiClient.java that allows attackers with the ability to control the HTTP server (Jenkins) queried in preparation of job import to read arbitrary files, perform a denial of service attack, etc." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003015,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-905%20(1)"  -sie -u

echo "Importing CVE-2018-10237 (209 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-10237 -r https://github.com/google/guava/ -e f89ece5721b2f637fe754937ff1f3c86d80bb196  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-10237,https://groups.google.com/forum/#!topic/guava-announce/xqWALw4W1vs/discussion"  -sie -u

echo "Importing CVE-2014-3678 (210 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3678 -r https://github.com/jenkinsci/monitoring-plugin/ -e f0f6aeef2032696c97d4b015dd51fa2b841b0473  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32325,https://jenkins.io/security/advisory/2014-10-01/"  -sie -u

echo "Importing HADOOP-12001 (211 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-12001 -r https://github.com/apache/hadoop/ -e 58d3a9aaf65310aba9b4300ef0cacd58ebfdb6e:2.8,722aa1db1f2ac3db0e70063022436a90f90643f:3.1,98f9d6fee112d95aab680fc7f27b815b2e698a5:2.7  -descr "Fixed LdapGroupsMapping to include configurable Posix UID and GID attributes during the search. Description: In HADOOP-9477, posixGroup support was added. In HADOOP-10626, a limit on the returned attributes was added to speed up queries. Limiting the attributes can break the SEARCH_CONTROLS object in the context of the isPosix block, since it only asks LDAP for the groupNameAttr. Fixed Version/s: 2.8.0, 3.0.0-alpha1, 2.7.6." -links "https://issues.apache.org/jira/browse/HADOOP-12001,http://hadoop.apache.org/docs/r2.7.6/hadoop-project-dist/hadoop-common/releasenotes.html"  -sie -u

echo "Importing CVE-2018-17228 (212 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17228 -r https://github.com/narkisr/nmap4j/ -e 06b58aa3345d2f977553685a026b93e61f0c491e  -links "https://snyk.io/vuln/SNYK-JAVA-ORGNMAP4J-72402,https://github.com/narkisr/nmap4j/issues/9"  -sie -u

echo "Importing CVE-2018-12022 (213 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12022 -r https://github.com/FasterXML/jackson-databind/ -e 7487cf7eb14be2f65a1eb108e8629c07ef45e0a:2.8.11,28badf7ef60ac3e7ef151cd8e8ec010b8479226:2.7.9  -descr "Block polymorphic deserialization of types from Jodd-db library. Description : There is a potential remote code execution (RCE) vulnerability, if user is 1. handling untrusted content (where attacker can craft JSON), 2. using 'Default Typing' feature (or equivalent; polymorphic value with base type of java.lang.Object 3. has jodd-db (https://jodd.org/db/) jar in classpath 4. allows connections from service to untrusted hosts (where attacker can run an LDAP service). (note: steps 1 and 2 are common steps as explained in https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062). To solve the issue, one type from Jodd database component is blacklisted to avoid their use as 'serialization gadgets'." -links "https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.8,https://github.com/FasterXML/jackson-databind/issues/2052"  -sie -u

echo "Importing CVE-2018-1336 (214 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1336 -r https://github.com/apache/tomcat/ -e 92cd494555598e99dd691712e8ee426a2f9c2e93  -descr "A bug in the UTF-8 decoder can lead to DoS. An improper handing of overflow in the UTF-8 decoder with supplementary characters can lead to an infinite loop in the decoder causing a Denial of Service. Affects: 7.0.28 to 7.0.88; 8.0.0.RC1 to 8.0.51; 8.5.0 to 8.5.30; 9.0.0.M1 to 9.0.7." -links "https://tomcat.apache.org/security-9.html"  -sie -u

echo "Importing CVE-2017-1000388 (215 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000388 -r https://github.com/jenkinsci/depgraph-view-plugin/ -e d442ff671965c279770b28e37dc63a6ab73c0f0e  -links "https://jenkins.io/security/advisory/2017-10-23/,https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32193"  -sie -u

echo "Importing CVE-2014-2068 (216 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2068 -r https://github.com/jenkinsci/jenkins -e 0530a6645aac10fec005614211660e98db44b5eb  -sie -u

echo "Importing CVE-2018-8038 (217 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8038 -r https://github.com/apache/cxf-fediz/ -e b6ed9865d0614332fa419fe4b6d0fe81bc2e660d  -descr "Apache CXF Fediz is vulnerable to DTD based XML attacksThis vulnerability affects all versions of Apache CXF Fediz prior to 1.4.4.Description:Apache CXF Fediz is a subproject of Apache CXF which implements theWS-Federation Passive Requestor Profile for SSO specification.In 2015, a security advisory CVE-2015-5175 was issued for Apache CXF Fediz, titled 'Apache CXF Fediz application plugins are vulnerable to Denial ofService (DoS) attacks'. This was due to the fact that Document TypeDeclarations (DTDs) were not disabled when parsing the response from theIdentity Provider (IdP).The fix for advisory CVE-2015-5175 in Apache CXF Fediz 1.1.3 and 1.2.1 prevented DoS style attacks via DTDs. However, it did not fully disable DTDs,meaning that the Fediz plugins could potentially be subject to a DTD-basedXML attack.In addition, the Apache CXF Fediz IdP is also potentially subject to DTD-basedXML attacks for some of the WS-Federation request parameters.This has been fixed in revision:https://github.com/apache/cxf-fediz/commit/b6ed9865d0614332fa419fe4b6d0fe81bc2e660dMigration:Apache CXF Fediz users should upgrade to 1.4.4 as soon as possible." -links "https://cxf.apache.org/security-advisories.data/CVE-2018-8038.txt.asc?version=1&modificationDate=1530712328121&api=v2,https://cxf.apache.org/security-advisories.html"  -sie -u

echo "Importing CVE-2017-7660 (218 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7660 -r https://github.com/apache/lucene-solr -e 9f91c619a35db89544f5c85795df4128c9f0d96:branch_5x,e3b0cfff396a7f92a4f621d598780116da916f3:branch_6x,2f5ecbcf9ed7a3a4fd37b5c55860ad8eace1bea:branch_5_5,e912b7cb5c68fbb87b874d41068cf5a3aea17da0  -sie -u

echo "Importing CVE-2017-14735 (219 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-14735 -r https://github.com/nahsra/antisamy -e 82da009e733a989a57190cd6aa1b6824724f6d36  -sie -u

echo "Importing CVE-2016-1181 (220 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1181 -r https://github.com/kawasima/struts1-forever -e eda3a79907ed8fcb0387a0496d0cb14332f250e8  -sie -u

echo "Importing CVE-2013-0158 (221 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-0158 -r https://github.com/jenkinsci/jenkins -e 4895eaafca468b7f0f1a3166b2fca7414f0d5da5,3dc13b957b14cec649036e8dd517f0f9cb21fb04,94a8789b699132dd706021a6be1b78bc47f19602,a9aff088f327278a8873aef47fa8f80d3c5932fd,c3d8e05a1b3d58b6c4dcff97394cb3a79608b4b2  -sie -u

echo "Importing 2012-05-05 (222 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b 2012-05-05 -r https://github.com/google/gson -e 1103bda23acb1719364e834a4545739ec2f76cd0  -descr "Security bug related to denial of service attack with Java HashMap String collisions. Fixed in release 2.2." -links "https://github.com/google/gson/blob/master/CHANGELOG.md"  -sie -u

echo "Importing CVE-2015-5531 (223 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5531 -r https://github.com/elastic/elasticsearch -e df1427a2935237fb61fc641984f9c76478627fec  -sie -u

echo "Importing CVE-2017-14063 (224 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-14063 -r https://github.com/AsyncHttpClient/async-http-client -e eb9e3347e45319be494db24d285a2aee4396f5d3  -sie -u

echo "Importing CVE-2012-0393 (225 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-0393 -r https://github.com/apache/struts -e 9cad25f258bb2629d263f828574d2671366c238d  -sie -u

echo "Importing CVE-2016-5007-SEC (226 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-5007-SEC -r https://github.com/spring-projects/spring-security -e e4c13e3c0ee7f06f59d3b43ca6734215ad7d8974  -descr "Both Spring Security and the Spring Framework rely on URL pattern mappings for authorization and for mapping requests to controllers respectively.Differences in the strictness of the pattern matching mechanisms, for example with regards to space trimming in path segments, can lead Spring Security to not recognize certain paths as not protected that are in fact mapped to Spring MVC controllers that should be protected.The problem is compounded by the fact that the Spring Framework provides richer features with regards to pattern matching as well as by the fact that pattern matching in each Spring Security and the Spring Framework can easily be customized creating additional differences." -links "https://pivotal.io/security/cve-2016-5007"  -sie -u

echo "Importing CVE-2018-1000844 (227 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000844 -r https://github.com/square/retrofit/ -e 97057aaae42e54bfbee8acfa8af7dcf37e812342  -links "https://snyk.io/vuln/SNYK-JAVA-COMSQUAREUPRETROFIT2-72719,https://github.com/square/retrofit/pull/2735"  -sie -u

echo "Importing CVE-2017-12624 (228 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12624 -r https://github.com/apache/cxf -e 896bd961cbbb6b8569700e5b70229f78f94ad9d:3.1.x-fixes,8bd915bfd7735c248ad660059c6b6ad26cdbcdf6  -sie -u

echo "Importing CVE-2014-3584 (229 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3584 -r https://github.com/apache/cxf -e 0b3894f57388b9955f2c33b2295223f2835cd7b3  -sie -u

echo "Importing HTTPCLIENT-1803 (230 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HTTPCLIENT-1803 -r https://github.com/apache/httpcomponents-client -e 0554271750599756d4946c0d7ba43d04b1a7b22:4.x  -descr "When using URIBuilder's constructor with a malformed url argument, host passed in by setHost call not honored. The string passed into the constructor is treated as path, not verifying the presence of a leading / character. This causes a security vulnerability where the user-provided path can be used to override the host, resulting in giving network access to a sensitive environment. Fixed in version 4.5.3" -links "https://issues.apache.org/jira/browse/HTTPCLIENT-1803"  -sie -u

echo "Importing CVE-2017-1000400 (231 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000400 -r https://github.com/jenkinsci/jenkins/ -e b2083a387a5bdb6f7ee7f7c81a1f6312aca2a558  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32183,https://jenkins.io/security/advisory/2017-10-11/"  -sie -u

echo "Importing CVE-2015-7940 (232 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-7940 -r http://git.bouncycastle.org/repositories/bc-java -e e25e94a046a6934819133886439984e2fecb2b04,5cb2f0578e6ec8f0d67e59d05d8c4704d8e05f83  -sie -u

echo "Importing CVE-2018-1263 (233 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1263 -r https://github.com/spring-projects/spring-integration-extensions/ -e d10f537283d90eabd28af57ac97f860a3913bf9b  -descr "Unsafe Unzip with spring-integration-zip. Description: spring-integration-zip , versions prior to 1.0.2, exposes an arbitrary file write vulnerability, that can be achieved using a specially crafted zip archive (affects other archives as well, bzip2, tar, xz, war, cpio, 7z), that holds path traversal filenames. So when the filename gets concatenated to the target extraction directory, the final path ends up outside of the target folder. The previous CVE-2018-1261 prevented the framework itself from writing the file. While the framework itself now does not write such files, it does present the errant path to the user application, which could inadvertently write the file using that path. This specifically applies to the unzip transformer. This can only happen if an application using this library accepts and unpacks zip files from untrusted sources. Affected Pivotal Products and Versions: Spring Integration Zip Community Extension Project versions 1.0.1.RELEASE and earlier. Mitigation: Upgrade to the 1.0.2.RELEASE Or do not unzip untrusted zip files." -links "https://pivotal.io/security/cve-2018-1263"  -sie -u

echo "Importing CVE-2018-1337 (234 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1337 -r https://github.com/apache/directory-ldap-api/ -e 075b70a733d7af150b3d85684149ff5f029f7fd:2.0,5faa6a71606a22a7503d401911875ec3a355cac:1.0.x  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEDIRECTORYAPI-32413,https://bugzilla.redhat.com/show_bug.cgi?id=1599886,https://lists.apache.org/thread.html/d66081195e9a02ee7cc20fb243b60467d1419586eed28297d820768f@%3Cdev.directory.apache.org%3E"  -sie -u

echo "Importing CVE-2015-0264 (235 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0264 -r https://github.com/apache/camel -e 1df559649a96a1ca0368373387e542f46e4820da  -sie -u

echo "Importing CVE-2016-4800 (236 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4800 -r https://github.com/eclipse/jetty.project -e 97af3d663fd22343129e8364d601640649d9eaea  -descr "Jetty 9.3.0 to 9.3.8 inclusive is vulnerable to an aliasing issue when running on Windows platform. The vulnerability allows raw file resources protected by security constraints or in WEB-INF to be revealed. It was reported that Jetty path normalization mechanism implemented in PathResource class and introduced in Jetty versions 9.3.x is vulnerable to malicious URL requests containing specific escaped characters. Malicious user can gain access to protected resources (e.g. WEB-INF and META-INF folders and their contents) and defeat application filters or other security constraints implemented in the servlet configuration. Only affected Jetty 9.3.0-9.3.8, please upgrade to 9.3.9. (see http://www.ocert.org/advisories/ocert-2016-001.html)" -links "http://www.ocert.org/advisories/ocert-2016-001.html"  -sie -u

echo "Importing CVE-2014-0086 (237 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0086 -r https://github.com/pslegr/core-1 -e 8131f15003f5bec73d475d2b724472e4b87d0757  -sie -u

echo "Importing CVE-2018-1000615 (238 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000615 -r https://github.com/opennetworkinglab/onos/ -e 1a783729a1d7e0cd59d59a8dd3a73cdd6ac0f30d  -links "https://snyk.io/vuln/SNYK-JAVA-ORGONOSPROJECT-32421,http://gms.cl0udz.com/OVSDB_DOS.pdf"  -sie -u

echo "Importing CVE-2018-1190 (239 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1190 -r https://github.com/cloudfoundry/uaa -e 96fe26711f8f8855d2994a531447f730afd61844  -descr "A cross-site scripting (XSS) attack is possible in the clientId parameter of a request to the UAA OpenID Connect check session iframe endpoint used for single logout session management. Users of affected versions should apply the following mitigation or upgrade: cf-release: 270, UAA release: 3.20.2, UAA bosh release: 30.8, 45.0" -links "https://www.cloudfoundry.org/cve-2018-1190/"  -sie -u

echo "Importing CVE-2017-5643 (240 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5643 -r https://github.com/apache/camel -e 2c6964ae94d8f9a9c9a32e5ae5a0b794e8b8d3b:2.17,87c92b7b38890c217bc76f2c55036e6a5cca9a0:2.18,8afc5d1757795fde715902067360af5d90f046d:2.19,ec3d0db81ba061b27e934d5ff56e9baca0049eb:2.18,9f7376abbff7434794f2c7c2909e02bac232fb5:2.18  -descr "The Validation Component of Apache Camel evaluates DTD headers of XML stream sources, although a validation against XML schemas (XSD) is executed. Remote attackers can use this feature to make Server-Side Request Forgery (SSRF) attacks by sending XML documents with remote DTDs URLs or XML External Entities (XXE).  The vulnerability is not given for SAX or StAX sources. Versions Affected: Camel 2.17.0 to 2.17.5, Camel 2.18.0 to 2.18.2 The unsupported Camel 2.x (2.16 and earlier) versions may be also affected. Mitigation: 2.17.x users should upgrade to 2.17.6, 2.18.x users should upgrade to 2.18.3. " -links "http://camel.apache.org/security-advisories.data/CVE-2017-5643.txt.asc?version=1&modificationDate=1489652454000&api=v2"  -sie -u

echo "Importing CVE-2018-14658 (241 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-14658 -r https://github.com/keycloak/keycloak/ -e a957e118e6efb35fe7ef3a62acd66341a6523cb7  -links "https://snyk.io/vuln/SNYK-JAVA-ORGKEYCLOAK-72619,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14658"  -sie -u

echo "Importing CVE-2016-4430 (242 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4430 -r https://github.com/apache/struts -e b28b78c062f0bf3c79793a25aab8c9b6c12bce6e  -sie -u

echo "Importing CVE-2017-1000395 (243 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000395 -r https://github.com/jenkinsci/jenkins/ -e 7b1f8e96a8d97dd09e5e093fcdb010b3295acc77  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32188,https://jenkins.io/security/advisory/2017-10-11/"  -sie -u

echo "Importing CVE-2017-7657 (244 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7657 -r https://github.com/eclipse/jetty.project/ -e a285deea42fcab60d9edcf994e458c238a348b55  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSEJETTY-32384,https://bugs.eclipse.org/bugs/show_bug.cgi?id=535668"  -sie -u

echo "Importing CVE-2018-8037 (245 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8037 -r https://github.com/apache/tomcat/ -e ed4b9d791f9470e4c3de691dd0153a9ce431701b  -descr "Due to a mishandling of close in NIO/NIO2 connectors user sessions can get mixed up. A bug in the tracking of connection closures can lead to reuse of user sessions in a new connection." -links "https://tomcat.apache.org/security-9.html"  -sie -u

echo "Importing CVE-2019-1003004 (246 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003004 -r https://github.com/jenkinsci/jenkins/ -e 8c490d14c4ffe6162f6e97d25a66612330fe2ace,da135e7ecb72469c17a47640314e424e314269b0  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003004,https://jenkins.io/security/advisory/2019-01-16/#SECURITY-901"  -sie -u

echo "Importing CVE-2017-5645 (247 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5645 -r https://github.com/apache/logging-log4j2 -e 5dcc19215827db29c993d0305ee2b0d8dd05939d  -sie -u

echo "Importing CVE-2018-8027 (248 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8027 -r https://github.com/apache/camel/ -e 9f7376abbff7434794f2c7c2909e02bac232fb5:2.18.3,87c92b7b38890c217bc76f2c55036e6a5cca9a0:2.18.3,ec3d0db81ba061b27e934d5ff56e9baca0049eb:2.18.3,3fe03e361725b66c1c3eaa40bb11577fb3dc17b:2.20,2c6964ae94d8f9a9c9a32e5ae5a0b794e8b8d3b:2.17.6,24eefa559fe6b310629d2bf00663d2679ec81b9:2.21,99cbcd78b7e64083fae1d9552ead7425a90994b:2.17.6,8afc5d1757795fde715902067360af5d90f046d:2.20,9c6a8f61de40c20f28240fbb2af4cb425793d41:2.21,2e8f21dec883b083ddcdddd802847b4c378a61a:2.22,8467d644813a62f3a836c0c7dee8cf5a41de3c0:2.22,22c355bb4ffb500405499d189db30932ca5aac9:2.17.6  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHECAMEL-32467,https://lists.apache.org/thread.html/77f596fc63e63c2e9adcff3c34759b32c225cf0b582aedb755adaade@%3Cdev.camel.apache.org%3E,http://camel.apache.org/security-advisories.data/CVE-2018-8027.txt.asc,https://issues.apache.org/jira/browse/CAMEL-10894,https://issues.apache.org/jira/browse/CAMEL-12444"  -sie -u

echo "Importing CVE-2018-11786 (249 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11786 -r https://github.com/apache/karaf -e 24fb477ea886e8f294dedbad98d2a2c4cb2a44f9  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKARAFSHELL-72392,https://issues.apache.org/jira/browse/KARAF-5427,https://lists.apache.org/thread.html/5b7ac762c6bbe77ac5d9389f093fc6dbf196c36d788e3d7629e6c1d9@%3Cdev.karaf.apache.org%3E"  -sie -u

echo "Importing CVE-2012-0391 (250 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-0391 -r https://github.com/apache/struts -e b4265d369dc29d57a9f2846a85b26598e83f3892,5f54b8d087f5125d96838aafa5f64c2190e6885b  -sie -u

echo "Importing CVE-2013-4378 (251 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4378 -r https://github.com/javamelody/javamelody/ -e aacbc46151ff4ac1ca34ce0899c2a6113071c66e  -sie -u

echo "Importing CVE-2016-6802 (252 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6802 -r https://github.com/apache/shiro -e b15ab927709ca18ea4a02538be01919a19ab65af  -sie -u

echo "Importing CVE-2018-1000134 (253 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000134 -r https://github.com/pingidentity/ldapsdk -e 8471904a02438c03965d21367890276bc25fa5a6  -links "https://snyk.io/vuln/SNYK-JAVA-COMUNBOUNDID-32143,https://nawilson.com/2018/03/19/cve-2018-1000134-and-the-unboundid-ldap-sdk-for-java/,https://bugzilla.redhat.com/show_bug.cgi?id=1557531"  -sie -u

echo "Importing CVE-2015-5172 (254 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5172 -r https://github.com/cloudfoundry/uaa -e cd31cc397fe17389d95b83d6a9caa46eebc54faf  -descr "Password Reset Link not expiring. Old password reset links working even after a password change. Deployments enabled for integration via SAML or LDAP are not affected." -links "https://www.cloudfoundry.org/cve-2015-5170-5173/"  -sie -u

echo "Importing CVE-2018-1000180 (255 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000180 -r https://github.com/bcgit/bc-java/ -e 22467b6e8fe19717ecdf201c0cf91bacf04a55ad,73780ac522b7795fc165630aba8d5f5729acc839  -links "https://snyk.io/vuln/SNYK-JAVA-ORGBOUNCYCASTLE-32369,https://www.bountysource.com/issues/58293083-rsa-key-generation-computation-of-iterations-for-mr-primality-test,https://www.bouncycastle.org/jira/browse/BJA-694"  -sie -u

echo "Importing CVE-2018-1322 (256 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1322 -r https://github.com/apache/syncope/ -e 44a5ca0fbd357b8b5d81aa9313fb01cca30d8ad:1.2.11,735579b6f987b407049ac1f1da08e675d957c3e:2.0.8,7b168c142b09c3b03e39f1449211e7ddf026a14:master  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESYNCOPE-32139,https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1322,http://syncope.apache.org/security.html#CVE-2018-1322:_Information_disclosure_via_FIQL_and_ORDER_BY_sorting"  -sie -u

echo "Importing CVE-2013-2115 (257 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2115 -r https://github.com/apache/struts -e d7804297e319c7a12245e1b536e565fcea6d650:STRUTS_2_3_14_2,fed4f8e8a4ec69b5e7612b92d8ce3e476680474:STRUTS_2_3_14_2,d934c6e7430b7b98e43a0a085a2304bd31a75c3d  -sie -u

echo "Importing CVE-2017-3163 (258 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-3163 -r https://github.com/apache/lucene-solr -e ae789c252687dc8a18bfdb677f2e6cd14570e4d:branch_5_5,7088137d52256354a52ed86547b9faa0e704293:branch_6x,3a4f885b18bc963a8326c752bd229497908f1db:branch_6_4,6f598d24692a89da9b5b671be6cf4b947aa39266  -descr "Apache Solr provides a 'replication' handler which supports operations related to querying the state of an index as well as copying files associated with the index. https://cwiki.apache.org/confluence/display/solr/Index+Replication <https://cwiki.apache.org/confluence/display/solr/Index+Replication> This handler supports an HTTP API (/replication?command=filecontent&file=<file_name>) which is vulnerable to path traversal attack. Specifically, this API does not perform any validation of the user specified file_name parameter. This can allow an attacker to download any file readable to Solr server process even if it is not related to the actual Solr index state. https://www.owasp.org/index.php/Path_Traversal (see https://issues.apache.org/jira/browse/SOLR-10031)  4.x, 3.x and 1.4 users should upgrade to a supported version of Solr or setup proper firewalling, or disable the ReplicationHandler if not in use." -links "https://wiki.apache.org/solr/SolrSecurity"  -sie -u

echo "Importing CVE-2013-4366 (259 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4366 -r https://github.com/apache/httpcomponents-client -e 08140864e3e4c0994e094c4cf0507932baf6a66:master  -sie -u

echo "Importing CVE-2015-1776 (260 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1776 -r https://github.com/apache/hadoop -e 6b710a42e00acca405e085724c89cda016cf7442  -sie -u

echo "Importing CVE-2017-2654 (261 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-2654 -r https://github.com/jenkinsci/email-ext-plugin/ -e af2cc9bf649781c3c84c6891298db0d8601b193d  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32468,https://jenkins.io/security/advisory/2017-03-20/"  -sie -u

echo "Importing CVE-2018-11047 (262 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11047 -r https://github.com/cloudfoundry/uaa/ -e 2906057dae995024576ce6afdc20abd85569514:4.19.2,81aeb7a3aa048ea086c494f725d643e48dd9266:4.10.2,aba1fb5f18e0d628628b2d960fc6d0cc62d86f5:4.7.6,bbbba5aec514ad88e7d1e168a2519c80229f02f:4.12.4,a1d523c7f150e56bf06df8b83ed1d416d6c1d3b:4.5.7  -descr "UAA accepts refresh token as access token on admin endpoints" -links "https://www.cloudfoundry.org/blog/cve-2018-11047/"  -sie -u

echo "Importing CVE-2014-9970 (263 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-9970 -r https://github.com/jboss-fuse/jasypt/ -e 8e62852a8018978ee19d39056c650fb66ffa0ff6  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJASYPT-31668,https://www.securitytracker.com/id/1039744"  -sie -u

echo "Importing CVE-2018-1295 (264 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1295 -r https://github.com/apache/ignite/ -e 340569b8f4e14a4cb61a9407ed2d9aa4a20bdf49  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEIGNITE-32200,https://lists.apache.org/thread.html/45e7d5e2c6face85aab693f5ae0616563132ff757e5a558da80d0209@%3Cdev.ignite.apache.org%3E"  -sie -u

echo "Importing CVE-2016-2402 (265 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2402 -r https://github.com/square/okhttp -e 3ccb46dd16b6ec98f70b0ee53eafe5ed6380891e,784fabac7d1586a5614bd4bc8854fd62850dbe26,5377f25d9eed755328216912ef5e922c93e14f3:2.x  -sie -u

echo "Importing CVE-2014-3612 (266 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3612 -r https://github.com/apache/activemq -e 0b5231ada5ce365b41832ba8752ee210145d1cbe  -descr "The LDAPLoginModule implementation in the Java Authentication and Authorization Service (JAAS) in Apache ActiveMQ 5.x before 5.10.1 allows remote attackers to bypass authentication by logging in with an empty password and valid username, which triggers an unauthenticated bind. NOTE: this identifier has been SPLIT per ADT2 due to different vulnerability types. See CVE-2015-6524 for the use of wildcard operators in usernames. (see https://issues.apache.org/jira/browse/AMQ-5345)" -sie -u

echo "Importing CVE-2018-1000125 (267 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000125 -r https://github.com/inversoft/prime-jwt -e 0d94dcef0133d699f21d217e922564adbb83a227  -sie -u

echo "Importing CVE-2015-3271 (268 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-3271 -r https://github.com/apache/tika -e 98672cdd92b6325ff78c763955a7c045b364095b  -descr "Apache Tika server (aka tika-server) in Apache Tika 1.9 might allow remote attackers to read arbitrary files via the HTTP fileUrl header. (see also https://issues.apache.org/jira/browse/TIKA-1690) " -links "https://nvd.nist.gov/vuln/detail?vulnId=2015-3271"  -sie -u

echo "Importing CVE-2016-0818 (269 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0818 -r https://android.googlesource.com/platform//external/conscrypt -e 4c9f9c2201116acf790fca25af43995d29980ee0,c4ab1b959280413fb11bf4fd7f6b4c2ba38bd779  -sie -u

echo "Importing CVE-2018-8018 (270 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8018 -r https://github.com/apache/ignite/ -e 82a7b8209fcf56971d12cb10410a38ed632215b:2.6,bc374f85ca4a5e69572902d2167fe6bedebd40a:master  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEIGNITE-32428,https://lists.apache.org/thread.html/e0fdf53114a321142ecfa5cfa17658090f0b4e1677de431e329b37ab@%3Cdev.ignite.apache.org%3E"  -sie -u

echo "Importing CVE-2018-1304 (271 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1304 -r https://github.com/apache/tomcat/ -e 723ea6a5bc5e7bc49e5ef84273c3b3c164a6a4fd  -links "https://tomcat.apache.org/security-9.html,https://tomcat.apache.org/security-7.html,https://tomcat.apache.org/security-8.html,https://bz.apache.org/bugzilla/show_bug.cgi?id=62067"  -sie -u

echo "Importing CVE-2019-1003010 (272 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003010 -r https://github.com/jenkinsci/git-plugin/ -e f9152d943936b1c6b493dfe750d27f0caa7c0767  -descr "A cross-site request forgery vulnerability exists in Jenkins Git Plugin 3.9.1 and earlier in src/main/java/hudson/plugins/git/GitTagAction.java that allows attackers to create a Git tag in a workspace and attach corresponding metadata to a build record." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003010,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1095"  -sie -u

echo "Importing CVE-2014-3488 (273 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3488 -r https://github.com/netty/netty -e 2fa9400a59d0563a66908aba55c41e7285a04994  -sie -u

echo "Importing CVE-2018-15531 (274 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-15531 -r https://github.com/javamelody/javamelody/ -e ef111822562d0b9365bd3e671a75b65bd0613353  -links "https://snyk.io/vuln/SNYK-JAVA-NETBULLJAVAMELODY-72410,https://jenkins.io/security/advisory/2018-09-25/"  -sie -u

echo "Importing CVE-2017-1000487 (275 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000487 -r https://github.com/codehaus-plexus/plexus-utils/ -e b38a1b3a4352303e4312b2bb601a0d7ec6e28f41  -links "https://vulners.com/cve/CVE-2017-1000487"  -sie -u

echo "Importing CVE-2013-4152 (276 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4152 -r https://github.com/spring-projects/spring-framework -e 7576274874deeccb6da6b09a8d5bd62e8b5538b7  -sie -u

echo "Importing CVE-2013-1879 (277 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-1879 -r https://github.com/apache/activemq -e 148ca81dcd8f14cfe2ff37012fd1aa42518f02dc  -sie -u

echo "Importing CVE-2016-2141 (278 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2141 -r https://github.com/belaban/JGroups/ -e 38a882331035ffed205d15a5c92b471fd09659c:master,fba182c14075789e1d2c976d50d9018c671ad0b:3.6.10,c3ad22234ef84d06d04d908b3c94c0d11df8afd:2.6.22  -links "https://access.redhat.com/security/cve/cve-2016-2141,https://issues.jboss.org/browse/JGRP-2021"  -sie -u

echo "Importing CVE-2018-11777 (279 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11777 -r https://github.com/apache/hive/ -e f0419dfaabe31dd7802c37aeebab101265907e1:branch-3.1,00c0ee7bc4b8492476b377a6edafcc33411f14b:master,1a1d6ca1bc3ae840238dc345fa1eb2c7c28c8cb:branch-2.3  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEHIVE-72580,https://lists.apache.org/thread.html/963c8e2516405c9b532b4add16c03b2c5db621e0c83e80f45049cbbb@%3Cdev.hive.apache.org%3E"  -sie -u

echo "Importing CVE-2017-7656 (280 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7656 -r https://github.com/eclipse/jetty.project/ -e a285deea42fcab60d9edcf994e458c238a348b55  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSEJETTY-32383,https://bugs.eclipse.org/bugs/show_bug.cgi?id=535667,http://dev.eclipse.org/mhonarc/lists/jetty-announce/msg00123.html"  -sie -u

echo "Importing CVE-2017-8032 (281 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8032 -r https://github.com/cloudfoundry/uaa -e 4e4d653edb6b8f68e12b7c415e07e068b1574b8:3.6.13,2c10c43f04cf31e9f8f496cd218bfc773dfc149:3.9.15,ea8c0ce7740a5d756d9f11964f6a6b4df54cc3b2  -descr "Zone administrators are allowed to escalate their privileges when mapping permissions for an external provider." -links "https://www.cloudfoundry.org/cve-2017-8032/"  -sie -u

echo "Importing CVE-2018-1270 (282 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1270 -r https://github.com/spring-projects/spring-framework/ -e d3acf45ea4db51fa5c4cbd0bc0e7b6d9ef805e6:4.x,1db7e02de3eb0c011ee6681f5a12eb9d166fea8:5.x,e0de9126ed8cf25cf141d3e66420da94e350708:5.x  -descr "Spring Framework, versions 5.0.x prior to 5.0.5 and versions 4.3.x prior to 4.3.16, as well as older unsupported versions allow applications to expose STOMP over WebSocket endpoints with a simple, in-memory STOMP broker through the spring-messaging module. A malicious user (or attacker) can craft a message to the broker that can lead to a remote code execution attack. Affected : Spring Framework 5.0 to 5.0.4, Spring Framework 4.3 to 4.3.15, Older unsupported versions are also affected" -links "https://pivotal.io/security/cve-2018-1270"  -sie -u

echo "Importing CVE-2015-3208 (283 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-3208 -r https://github.com/apache/activemq-artemis -e 48d9951d879e0c8cbb59d4b64ab59d53ef88310d  -sie -u

echo "Importing CVE-2017-15695 (284 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-15695 -r https://github.com/apache/geode/ -e 49d28f93fd2ef069693ce15d124ef3a29f22fb7d,954ccb545d24a9c9a35cbd84023a4d7e07032de0,00be4f9774e1adf8e7ccc2664da8005fc30bb11d,6df14c8b1e3c644f9f810149e80bba0c2f073dab,90f8f6242927c5e16da64f38bba9abf3d450a305,aa469239860778eb46e09dd7b390aee08f152480,740289c61d60256c6270756bc84b9e24b76e4913  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEGEODE-32373,https://issues.apache.org/jira/browse/GEODE-3974"  -sie -u

echo "Importing CVE-2018-11087 (285 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11087 -r https://github.com/spring-projects/spring-amqp/ -e aff4d0aefcdb99726fd739abf3b9bb96df97b0f:1.7.10,444b74e95bb299af5e23ebf006fbb45d574fb95:2.1.0,d64e7fa3993dac577c0973e0caf8c31d27ef5e4:2.0.6  -descr "Description: The Spring RabbitMQ Java Client does not perform hostname validation. This means that SSL certificates of other hosts are blindly accepted as long as they are trusted. To exploit this vulnerability an attacker has to perform a man-in-the-middle (MITM) attack between a Java application using the Spring RabbitMQ Java Client and an RabbitMQ server it's connecting to. TLS normally protects users and systems against MITM attacks, it cannot if certificates from other trusted hosts are accepted by the client. Spring AMQP uses the RabbitMQ amqp-client java library for communication with RabbitMQ. It uses the RabbitConnectionFactoryBean to create/configure the connection factory.\n Affected Versions: \n - Spring-AMQP versions prior to 1.7.10 and 2.0.6 /n - RabbitMQ amqp-client versions prior to 4.8.0 and 5.4.0 .\n Mitigation: Users of affected versions should apply the following mitigation: \n - Upgrade to the 1.7.10.RELEASE or 2.0.6.RELEASE and set the enableHostnameValidation property to true. Override the transitive amqp-client version to at least 4.8.0 and 5.4.0, respectively. \n - The upcoming 2.1.0.RELEASE will set the property to true by default.\n - If you are using the amqp-client library directly to create a connection factory, refer to its javadocs for the enableHostnameValidation() method." -links "https://pivotal.io/security/cve-2018-11087,https://jira.spring.io/browse/AMQP-830"  -sie -u

echo "Importing CVE-2018-19859 (286 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-19859 -r https://github.com/OpenRefine/OpenRefine/ -e e243e73e4064de87a913946bd320fbbe246da656  -links "https://snyk.io/vuln/SNYK-JAVA-ORGOPENREFINE-72693,https://github.com/OpenRefine/OpenRefine/issues/1840"  -sie -u

echo "Importing CVE-2018-1331 (287 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1331 -r https://github.com/apache/storm/ -e e3652b44a377436256f77a2749ed133bbafd2fb:1.2,22a962073c5f12dc5ab281a15d93eb5efc31ab6:1.1,8ffa920d3894634aa078f0fdf6b02d270262caf:master,a6bf3e421d3d37a797e3bb374fcd20a00189feb:1.0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESTORM-32410,https://www.securitytracker.com/id/1041273,http://storm.apache.org/2018/06/04/storm122-released.html"  -sie -u

echo "Importing CVE-2017-15709 (288 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-15709 -r https://github.com/apache/activemq -e 5fa0bbd5156f29d97dcf48fd9fdb6a0488a8df1a,8ff18c5e254bf43395f2e0d7e3a1092b33ec646:5.14.x,d2e49be3a8f21d862726c1f6bc9e1caa6ee8b58:5.15.x  -sie -u

echo "Importing CVE-2012-6119 (289 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-6119 -r https://github.com/candlepin/candlepin -e f4d93230e58b969c506b4c9778e04482a059b08c  -sie -u

echo "Importing CVE-2017-7661 (290 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7661 -r https://github.com/apache/cxf-fediz -e acdbe8c213576792dd95d87315bcc181ea61b57f  -sie -u

echo "Importing CVE-2016-3088 (291 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3088 -r https://github.com/apache/activemq -e 3dd86d04e8b90ba309819317d19e7260d414d9e7  -descr "The Fileserver web application in Apache ActiveMQ 5.x before 5.14.0 allows remote attackers to upload and execute arbitrary files via an HTTP PUT followed by an HTTP MOVE request. (see https://issues.apache.org/jira/browse/AMQ-6276) and http://activemq.apache.org/security-advisories.data/CVE-2016-3088-announcement.txt" -sie -u

echo "Importing CVE-2015-0899 (292 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0899 -r https://github.com/kawasima/struts1-forever -e 212bb0f7c57617b7b9c44cb1e056bd1e597c8e16  -sie -u

echo "Importing CVE-2017-12634 (293 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12634 -r https://github.com/apache/camel -e 573ebd3de810cc7e239f175e1d2d6993f1f2ad0:camel-2.20.x,ad3c1ce9d8300c339cfa7d0f4a4dea691a94798:,2ae645e90edff3bcc1b958cb53ddc5e60a7f49f:camel-2.19.x,adc06a78f04c8d798709a5818104abe5a8ae4b3:camel-2.19.x  -sie -u

echo "Importing CVE-2016-4431 (294 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4431 -r https://github.com/apache/struts -e b28b78c062f0bf3c79793a25aab8c9b6c12bce6e  -sie -u

echo "Importing HADOOP-15212 (295 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-15212 -r https://github.com/apache/hadoop/ -e 6ea2a9389e8bd1b5aa35d01c5b1556f892181f1:2.7,2dd960de983a30bf0d9ee957bdb09f825f9d40a:3.10.0  -descr "Add independent secret manager method for logging expired tokens. Description: AbstractDelegationTokenSecretManager#removeExpiredToken has two phases. First phase synchronizes to collect expired tokens. Second phase loops over the collected tokens to log them while not holding the monitor. HDFS-13112 needs to acquire the namesystem lock during the second logging phase, which requires splitting the method apart to allow a method override. Fixed Version/s: 3.1.0, 2.10.0, 2.9.1, 3.0.1, 2.8.4, 2.7.6." -links "https://issues.apache.org/jira/browse/HADOOP-15212,http://hadoop.apache.org/docs/r2.7.6/hadoop-project-dist/hadoop-common/releasenotes.html"  -sie -u

echo "Importing CVE-2017-7662 (296 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7662 -r https://github.com/apache/cxf-fediz -e c68e4820816c19241568f4a8fe8600bffb0243cd  -sie -u

echo "Importing CVE-2018-17184 (297 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17184 -r https://github.com/apache/syncope/ -e 73aed0a741b1255f45893e3cada650147335073:2.0.11,36fb466afd64894170fa5e2e030ce6895120b1a:master,b25a8834db2cc7ea45707a1218e85e047568427:2.1.0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESYNCOPE-72568,https://syncope.apache.org/security#CVE-2018-17184:_Stored_XSS"  -sie -u

echo "Importing CVE-2013-2035 (298 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2035 -r https://github.com/fusesource/hawtjni -e 92c266170ce98edc200c656bd034a237098b8aa5  -sie -u

echo "Importing CVE-2014-3558 (299 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3558 -r https://github.com/hibernate/hibernate-validator -e c9525ca544b1281e2b7c7347e86e87c86dc1dc6e,f97c2021a03c825abdeca1692f5be51e77e76a8f,e8c42b689df8c6752d635d02c6518da3fece3870,67fdff14831c035c25e098fe14bd86523d17f726,2c95d4ea0ef20977be249e31a4a4f4f4f71c945d,fd4eaed7fb930db6a5e4c03742b4b3adcfecc90e,7e7131939a4361a7cad3e77ab89a8462132c561c,c489416f699a46859c134796b3ccfea41ef3ce52  -sie -u

echo "Importing CVE-2013-2135 (300 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2135 -r https://github.com/apache/struts -e 54e5c912ebd9a1599bfcf7a719da17c28127bbe:STRUTS_2_3_14_3,711cf0201cdd319a38cf29238913312355db29ba,cfb6e9afbae320a4dd5bdd655154ab9fe5a92c1:STRUTS_2_3_14_3,01e6b251b4db78bfb7971033652e81d1af4cb3e:STRUTS_2_3_14_3,8b4fc81daeea3834bcbf73de5f48d0021917aa3:STRUTS_2_3_14_3  -sie -u

echo "Importing CVE-2018-1000616 (301 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000616 -r https://github.com/opennetworkinglab/onos/ -e af1fa39a53c0016e92c1de246807879c16f507d6  -links "https://snyk.io/vuln/SNYK-JAVA-ORGONOSPROJECT-32422,http://gms.cl0udz.com/Openconfig_xxe.pdf"  -sie -u

echo "Importing CVE-2014-0225 (302 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0225 -r https://github.com/spring-projects/spring-framework -e 8e096aeef55287dc829484996c9330cf755891a1,c6503ebbf7c9e21ff022c58706dbac5417b2b5eb  -descr "When processing user provided XML documents, the Spring Framework did not disable by default the resolution of URI references in a DTD declaration. This enabled an XXE attack." -links "http://pivotal.io/security/cve-2014-0225"  -sie -u

echo "Importing CVE-2018-1199 (303 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1199 -r https://github.com/spring-projects/spring-security -e cb8041ba67635edafcc934498ef82707157fd22:4.2.x,0eef5b4b425ab42b9fa0fde1a3f36a37b92558f:master,65da28e4bf62f58fb130ba727cbbd621b44a36d:4.1.x  -descr "Spring Security does not consider URL path parameters when processing security constraints. By adding a URL path parameter with special encodings, an attacker may be able to bypass a security constraint. The root cause of this issue is a lack of clarity regarding the handling of path parameters in the Servlet Specification (see below). Some Servlet containers include path parameters in the value returned for getPathInfo() and some do not. Spring Security uses the value returned by getPathInfo() as part of the process of mapping requests to security constraints. In this particular attack, different character encodings used in path parameters allows secured Spring MVC static resource URLs to be bypassed." -links "https://pivotal.io/security/cve-2018-1199"  -sie -u

echo "Importing JAVAMELODY-252 (304 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b JAVAMELODY-252 -r https://github.com/javamelody/javamelody -e 00ff3490878e78f3f8c9eb65efb054f85f6058f8  -descr "A cross site scripting vulnerability has been identified in this package. Particulary, URL parameters such as SessionID are output to HTML unescaped, which allows the injection of malicious javascript." -links "https://github.com/javamelody/javamelody/issues/252"  -sie -u

echo "Importing CVE-2017-1000355 (305 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000355 -r https://github.com/jenkinsci/jenkins/ -e 701ea95a52afe53bee28f76a3f96eb0e578852e9  -links "https://jenkins.io/security/advisory/2017-04-26/,https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32195"  -sie -u

echo "Importing CVE-2016-1000031 (306 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000031 -r https://github.com/apache/commons-fileupload -e 02f6b2c4ef9aebf9cf8e55de8b90e73430b69385,388e824518697c2c8f9f83fd964621d9c2f8fc4c:b1_3:b1_3  -descr "There exists a Java Object in the Apache Commons FileUpload library that can be manipulated in such a way that when it is deserialized, it can write or copy files to disk in arbitrary locations. Furthermore, while the Object can be used alone, this new vector can be integrated with ysoserial to upload and execute binaries in a single deserialization call. This may or may not work depending on an application's implementation of the FileUpload library." -links "https://issues.apache.org/jira/browse/FILEUPLOAD-279"  -sie -u

echo "Importing CVE-2018-11776 (307 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11776 -r https://github.com/apache/struts -e b3bad5ea44f3fd9edb2cb491192c5900f46d45d:2.5.x,4a3917176de2df7f33a85511d067f31e50dcc1b:2.3.x,6efaf900d4ffb7be8a74065af5553bad2389f72:2.5.x,6e87474f9ad0549f07dd2c37d50a9ccd0977c6e:2.5.x  -sie -u

echo "Importing CVE-2017-7658 (308 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7658 -r https://github.com/eclipse/jetty.project -e a285deea42fcab60d9edcf994e458c238a348b55  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSEJETTY-32385,https://bugs.eclipse.org/bugs/show_bug.cgi?id=535669,https://github.com/eclipse/jetty.project/issues/2572,https://github.com/eclipse/jetty.project/issues/2529"  -sie -u

echo "Importing CVE-2018-1999040 (309 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999040 -r https://github.com/jenkinsci/kubernetes-plugin/ -e bf7a47847dfb5ef2d1e2a537e2eb9f28063988c6  -links "https://snyk.io/vuln/SNYK-JAVA-ORGCSANCHEZJENKINSPLUGINS-32458,https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1016"  -sie -u

echo "Importing CVE-2019-3774 (310 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-3774 -r https://github.com/spring-projects/spring-batch/ -e 8dc3bb7d3c3d0b1487e3ef3dcbdebda865d2b20e  -links "https://pivotal.io/security/cve-2019-3774,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKBATCH-73519"  -sie -u

echo "Importing CVE-2013-7251 (311 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7251 -r https://github.com/micromata/projectforge-webapp -e 422de35e3c3141e418a73bfb39b430d5fd74077e  -sie -u

echo "Importing CVE-2018-1000866 (312 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000866 -r https://github.com/jenkinsci/groovy-sandbox/ -e 0cd7ec12b7c56cfa3167d99c5f43147ce05449d3  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000866,https://jenkins.io/security/advisory/2018-10-29/#SECURITY-1186"  -sie -u

echo "Importing CVE-2016-1182 (313 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1182 -r https://github.com/kawasima/struts1-forever -e eda3a79907ed8fcb0387a0496d0cb14332f250e8  -sie -u

echo "Importing CVE-2017-12626 (314 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12626 -r https://github.com/apache/poi/ -e cd6236c74b55763a27e3e9b5f269c28bc9c98419,df3910135fd9c442b4e746e4b156362fd2e8d755,a07ed9e86474da98f204efadfd5b9327009a0d21,c7db66a30dfb6cbbd5812ff3ae4c90ed2d9b9a27  -sie -u

echo "Importing CVE-2016-3082 (315 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3082 -r https://github.com/apache/struts -e 6bd694b7980494c12d49ca1bf39f12aec3e03e2f  -sie -u

echo "Importing CVE-2017-5653 (316 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5653 -r https://github.com/apache/cxf -e fade9b81dabe27f864ca38e7b40f28fb44d6f165  -sie -u

echo "Importing CVE-2017-4974 (317 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4974 -r https://github.com/cloudfoundry/uaa -e 01edea6337c8ddb2ab80906aa1254d3c1dc02fb:2.7.4.x,74b9b270787aa602196d59d58893c3a6e09816f9,b6d6526cb89120043d390bf0274cd062e9fc452:3.9.x,5dc5ca9176ed5baa870680d99f37e7e559dddc5:3.6.x  -descr "An authorized user can use a blind SQL injection attack to query the contents of the UAA database." -links "https://cloudfoundry.org/cve-2017-4974/"  -sie -u

echo "Importing CVE-2016-5007 (318 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-5007 -r https://github.com/spring-projects/spring-framework -e a30ab30e4e9ae021fdda04e9abfc228476b846b5  -descr "Both Spring Security and the Spring Framework rely on URL pattern mappings for authorization and for mapping requests to controllers respectively.Differences in the strictness of the pattern matching mechanisms, for example with regards to space trimming in path segments, can lead Spring Security to not recognize certain paths as not protected that are in fact mapped to Spring MVC controllers that should be protected.The problem is compounded by the fact that the Spring Framework provides richer features with regards to pattern matching as well as by the fact that pattern matching in each Spring Security and the Spring Framework can easily be customized creating additional differences." -links "https://pivotal.io/security/cve-2016-5007"  -sie -u

echo "Importing CVE-2016-4464 (319 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4464 -r https://github.com/apache/cxf-fediz -e 0006581e9cacbeef46381a223e5671e524d416b6  -sie -u

echo "Importing CVE-2018-11797 (320 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11797 -r https://github.com/apache/pdfbox/ -e 4fa98533358c106522cd1bfe4cd9be2532af852:trunk,a6deb9d7ffec79986cac82345db724b343ca3e5:2.0.12,f7dc8eed7df007c88421919932e2d4de44d2ae2:1.8.16  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEPDFBOX-72426,https://www.apache.org/dist/pdfbox/2.0.12/RELEASE-NOTES.txt,https://www.apache.org/dist/pdfbox/1.8.16/RELEASE-NOTES.txt,https://lists.apache.org/thread.html/a9760973a873522f4d4c0a99916ceb74f361d91006b663a0a418d34a@%3Cannounce.apache.org%3E"  -sie -u

echo "Importing CVE-2017-8031 (321 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8031 -r https://github.com/cloudfoundry/uaa -e 66166d17781aa257ff77a2fb7c69f72d0b611be:4.7.x,1e2a746968cdac5b53164ca8955646e4257ecc7:3.20.x,20808046de8bbdc6fb2ac62829d4cc9d7a19f37:4.5.x  -descr "In some cases, the UAA allows an authenticated user for a particular client to revoke client tokens for other users on the same client. This occurs only if the client is using opaque tokens or JWT tokens validated using the check_token endpoint. A malicious actor could cause denial of service. Fixed in versions: 3.20.1, 4.5.3, 4.7.1" -links "https://www.cloudfoundry.org/cve-2017-8031/"  -sie -u

echo "Importing CVE-2017-8039 (322 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8039 -r https://github.com/spring-projects/spring-webflow -e ed5e8:2_4_6,df0ea:2_4_6,084b4:2_5_x  -sie -u

echo "Importing CVE-2018-1192 (323 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1192 -r https://github.com/cloudfoundry/uaa/ -e b599af2062aad5580661e035087fdd9bd266b92:4.15,a61bfabbad22f646ecf1f00016b448b26a60daf:4.5.x  -links "https://www.cloudfoundry.org/blog/cve-2018-1192/"  -sie -u

echo "Importing CVE-2013-5960 (324 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-5960 -r https://github.com/ESAPI/esapi-java-legacy -e b7cbc53f9cc967cf1a5a9463d8c6fef9ed6ef4f7  -links "https://github.com/esapi/esapi-java-legacy/issues/306,https://github.com/ESAPI/esapi-java-legacy/blob/develop/documentation/ESAPI-security-bulletin1.docx"  -sie -u

echo "Importing CVE-2014-2064 (325 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-2064 -r https://github.com/jenkinsci/jenkins -e fbf96734470caba9364f04e0b77b0bae7293a1ec  -sie -u

echo "Importing CVE-2018-1000055 (326 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000055 -r https://github.com/jenkinsci/android-lint-plugin/ -e 4a19f962ebde3f705880b0e8148731d8dac9db2d  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32162,https://jenkins.io/security/advisory/2018-02-05/"  -sie -u

echo "Importing CVE-2018-1000410 (327 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000410 -r https://github.com/jenkinsci/jenkins/ -e 7366cc50106442a021c5178cd101057ecc08f2c2  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000410,https://jenkins.io/security/advisory/2018-10-10/#SECURITY-765"  -sie -u

echo "Importing CVE-2018-1000107 (328 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000107 -r https://github.com/jenkinsci/ownership-plugin/ -e 42487df17cd272e504d3cd3e09abb4904f80dba2  -links "https://nvd.nist.gov/vuln/detail/CVE-2018-1000107,https://jenkins.io/security/advisory/2018-02-26/#SECURITY-498"  -sie -u

echo "Importing CVE-2016-6798 (329 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6798 -r https://github.com/apache/sling -e fb2719e8299fadddae62245482de112052a0e08c  -descr "In the XSS Protection API module before 1.0.12 in Apache Sling, the method XSS.getValidXML() uses an insecure SAX parser to validate the input string, which allows for XXE attacks in all scripts which use this method to validate user input, potentially allowing an attacker to read sensitive data on the filesystem, perform same-site-request-forgery (SSRF), port-scanning behind the firewall or DoS the application. (see https://issues.apache.org/jira/browse/SLING-5954)" -links "https://nvd.nist.gov/vuln/detail/CVE-2016-6798"  -sie -u

echo "Importing CVE-2014-0109 (330 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0109 -r https://github.com/apache/cxf -e f8ed98e684c1a67a77ae8726db05a04a4978a445  -sie -u

echo "Importing CVE-2013-4002 (331 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4002 -r https://github.com/apache/xerces2-j/ -e 628cbc7142ef9acfb61b8e571aab63504235849:Xerces-J_2_12_0-xml-schema-1.1,266e837852e0f0e3c8c1ad572b6fc4dbb4ded17:Xerces-J_2_12_0  -links "https://issues.apache.org/jira/browse/XERCESJ-1679"  -sie -u

echo "Importing NIFI-4436 (332 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b NIFI-4436 -r https://github.com/apache/nifi -e 0127b02617530491a1a55aa72395cee583083956,b6117743d4c1c1a37a16ba746b9edbbdd276d69f  -descr "NIFI-4436: Fixed bug that causes a deadlock when changing version of a PG. Before this patch, an update would obtain a write lock and then recurse downward through the child groups, obtaining write locks to update variable registries. At the same time, if a Processor is obtaining a Controller Service, it will obtain a Read Lock on the Process Group and then recurse upward through the ancestors, obtaining Read Lock. If the timing is right, we can have a group obtain a read lock, then try to obtain its parent's Read Lock. At the same time, an update to the group could hold the Write Lock on the Process Group and attempt to obtain a Write Lock on child (where the Processor lives), resulting in a deadlock. Remediation: Upgrade org.apache.nifi:nifi-framework-core to version 1.5.0 or higher." -links "https://issues.apache.org/jira/browse/NIFI-4436"  -sie -u

echo "Importing CVE-2013-6397 (333 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6397 -r https://github.com/apache/lucene-solr -e da34b18cb3092df4972e2b6fa5178d1059923910  -sie -u

echo "Importing CVE-2018-20059 (334 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-20059 -r https://github.com/pippo-java/pippo/ -e 9f36e5891c0b11f840e1e1561ae96d83ba9ce759  -links "https://snyk.io/vuln/SNYK-JAVA-ROPIPPO-72692,https://github.com/pippo-java/pippo/issues/486"  -sie -u

echo "Importing CVE-2017-2617 (335 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-2617 -r https://github.com/hawtio/hawtio/ -e 8cf6848f4d4d4917a4551c9aa49dc00f699eb569  -links "https://snyk.io/vuln/SNYK-JAVA-IOHAWT-32303,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2617"  -sie -u

echo "Importing CVE-2018-1274 (336 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1274 -r https://github.com/spring-projects/spring-data-commons/ -e 3d8576fe4e4e71c23b9e6796b32fd56e51182ee:2.0.x,371f6590c509c72f8e600f3d05e110941607fba:1.13.x  -descr "Spring Data Commons, versions prior to 1.13 to 1.13.10, 2.0 to 2.0.5, and older unsupported versions, contain a property path parser vulnerability caused by unlimited resource allocation. An unauthenticated remote malicious user (or attacker) can issue requests against Spring Data REST endpoints or endpoints using property path parsing which can cause a denial of service (CPU and memory consumption). Affected : Spring Data Commons 1.13 to 1.13.10 (Ingalls SR10), Spring Data REST 2.6 to 2.6.10 (Ingalls SR10), Spring Data Commons 2.0 to 2.0.5 (Kay SR5), Spring Data REST 3.0 to 3.0.5 (Kay SR5),Older unsupported versions are also affected" -links "https://pivotal.io/security/cve-2018-1274"  -sie -u

echo "Importing CVE-2016-4977 (337 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4977 -r https://github.com/spring-projects/spring-security-oauth -e fff77d3fea477b566bcacfbfc95f85821a2bdc2d  -descr "When processing authorization requests using the whitelabel views, the response_type parameter value was executed as Spring SpEL which enabled a malicious user to trigger remote code execution via the crafting of the value for response_type." -links "https://pivotal.io/security/cve-2016-4977"  -sie -u

echo "Importing CVE-2019-1003025 (338 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003025 -r https://github.com/jenkinsci/cloudfoundry-plugin/ -e 61208697f60b91ad7f03a4dcec391b6d2115abca  -descr "Cross-Site Request Forgery (CSRF)Descriptionorg.jenkins-ci.plugins:cloudfoundry can push apps to a Cloud Foundry platform at the end of a Jenkins build.Affected versions of this package are vulnerable to Cross-Site Request Forgery (CSRF) in AbstractCloudFoundryPushDescriptor.java that allows attackers with Overall/Read access to connect to an attacker-specified URL using attacker-specified credentials IDs obtained through another method, capturing credentials stored in Jenkins.RemediationUpgrade org.jenkins-ci.plugins:cloudfoundry to version 2.3.2 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-173714,https://jenkins.io/security/advisory/2019-02-19/#SECURITY-876"  -sie -u

echo "Importing CVE-2018-1324 (339 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1324 -r https://github.com/apache/commons-compress -e 2a2f1dc48e22a34ddb72321a4db211da91aa933b  -sie -u

echo "Importing CVE-2014-0193 (340 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0193 -r https://github.com/netty/netty -e 8599ab5bdb761bb99d41a975d689f74c12e4892b  -sie -u

echo "Importing CVE-2018-12972 (341 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12972 -r https://github.com/OpenTSDB/opentsdb -e a6a9ec4bc8a526951bc25bb19a145782bafaa8b0  -sie -u

echo "Importing CVE-2018-11248 (342 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11248 -r https://github.com/lingochamp/FileDownloader/ -e ff240b883490a84744705f9b4165719d7633f902  -links "https://snyk.io/vuln/SNYK-JAVA-COMLIULISHUOFILEDOWNLOADER-32291,https://github.com/lingochamp/FileDownloader/issues/1028"  -sie -u

echo "Importing CVE-2016-6194 (343 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6194 -r https://github.com/rabbitmq/rabbitmq-jms-client -e 95ae7401c0f007d5c8e6618ab009c171ce633916  -descr "ObjectMessage#getObject deserializes any value without performing input validation. Patched by limiting supported classes via a white list of package prefixes. By default all packages are trusted for backwards compatibility. Fixed in release 1.5.0 (see https://github.com/rabbitmq/rabbitmq-jms-client/issues/3)" -links "https://github.com/rabbitmq/rabbitmq-jms-client/pull/4"  -sie -u

echo "Importing CVE-2018-1000110 (344 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000110 -r https://github.com/jenkinsci/git-plugin -e a3d3a7eb7f75bfe97a0291e3b6d074aafafa86c9  -sie -u

echo "Importing CVE-2014-0168 (345 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0168 -r https://github.com/rhuss/jolokia -e 2d9b168cfbbf5a6d16fa6e8a5b34503e3dc42364  -sie -u

echo "Importing CVE-2018-1000068 (346 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000068 -r https://github.com/jenkinsci/jenkins -e 8830d68f5fe21f344be3496984bc4470bfcd0564  -sie -u

echo "Importing CVE-2018-15756 (347 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-15756 -r https://github.com/spring-projects/spring-framework/ -e 423aa28ed584b4ff6e5bad218c09beef5e91951:5.1.1,044772641d12b9281185f6cf50f8485b8747132:4.3.10,c8e320019ffe7298fc4cbeeb194b2bfd6389b6d:5.0.10  -descr "DoS Attack via Range Requests. Spring Framework, version 5.1, versions 5.0.x prior to 5.0.10, versions 4.3.x prior to 4.3.20, and older unsupported versions on the 4.2.x branch provide support for range requests when serving static resources through the ResourceHttpRequestHandler, or starting in 5.0 when an annotated controller returns an org.springframework.core.io.Resource. A malicious user (or attacker) can add a range header with a high number of ranges, or with wide ranges that overlap, or both, for a denial of service attack.This vulnerability affects applications that depend on either spring-webmvc or spring-webflux. Such applications must also have a registration for serving static resources (e.g. JS, CSS, images, and others), or have an annotated controller that returns an org.springframework.core.io.Resource.Spring Boot applications that depend on spring-boot-starter-web or spring-boot-starter-webflux are ready to serve static resources out of the box and are therefore vulnerable.Affected Pivotal Products and Versions:- Spring Framework 5.1- Spring Framework 5.0.0 to 5.0.9- Spring Framework 4.3 to 4.3.19- Older unsupported versions going back to 4.2 are also affectedMitigation:Users of affected versions should apply the following mitigation.- 5.1 users should upgrade to 5.1.1- 5.0.x users should upgrade to 5.0.10- 4.3.x users should upgrade to 4.3.20- 4.2.x users should upgrade to a supported branch.No further mitigation steps are necessary.Note the following when evaluating the impact:Support for Range requests was introduced in version 4.2. Therefore versions prior to 4.2 are not affected by this issue.Support for returning an org.springfamework.core.io.Resource from an annotated controller was introduced in 5.0. Therefore versions prior to 5.0 can only be impacted through a registration to serve static resources.History:2018-10-16: Initial vulnerability report published." -links "https://pivotal.io/security/cve-2018-15756"  -sie -u

echo "Importing CVE-2017-12629 (348 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12629 -r https://github.com/apache/lucene-solr/ -e d8000beebfb13ba0b6e754f84c760e11592d8d1:5.5.5,3bba91131b5257e64b9d0a2193e1e32a145b2a2:7.1,926cc4d65b6d2cc40ff07f76d50ddeda947e3cc:master,f9fd6e9e26224f26f1542224ce187e04c27b268:6.6.2,d28baa3fc5566b47f1ca7cc2ba1aba658dc634a:7.2  -links "https://lucene.apache.org/solr/news.html,https://snyk.io/vuln/SNYK-JAVA-ORGAPACHELUCENE-31569,https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESOLR-32013,https://snyk.io/vuln/SNYK-LINUX-LUCENESOLR-115218"  -sie -u

echo "Importing ZEPPELIN-2769 (349 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b ZEPPELIN-2769 -r https://github.com/apache/zeppelin -e 709c5a70a8f37277c9eea0a1c0c9195b5eb21a74  -sie -u

echo "Importing CVE-2018-8009 (350 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8009 -r https://github.com/apache/hadoop/ -e 6d7d192e4799b51931e55217e02baec14d49607:2,745f203e577bacb35b042206db94615141fa5e6:trunk,eaa2b8035b584dfcf7c79a33484eb2dffd3fdb1:2.7,6a4ae6f6eeed1392a4828a5721fa1499f65bdde:2.9,bd98d4e77cf9f7b2f4b1afb4d5e5bad0f6b2fde:3.0,12258c7cff8d32710fbd8b9088a930e3ce27432:2.8,fc4c20fc3469674cb584a4fb98bac7e3c2277c9:3.1,e3236a9680709de7a95ffbc11b20e1bdc95a860:trunk,1373e3d8ad60e4da721a292912cb69243bfdf47:2.9,65e55097da2bb3f2fbdf9ba1946da25fe58bec9:3.0,11a425d11a329010d0ff8255ecbcd1eb51b642e:3.1,cedc28d4ab2a27ba47e15ab2711218d96ec88d2:2,45a1c680c276c4501402f7bc4cebcf85a6fbc7f:2.7  -descr "Zip-Slip vulnerability for Apache Hadoop." -links "https://snyk.io/research/zip-slip-vulnerability"  -sie -u

echo "Importing CVE-2016-4436 (351 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4436 -r https://github.com/apache/struts -e 27ca165ddbf81c84bafbd083b99a18d89cc49ca7,237432512df0e27013f7c7b9ab59fdce44ca34a5  -descr "The method used to clean up action name can produce vulnerable payload based on crafted input which can be used by attacker to perform unspecified attack. Upgrade to latest version of the Apache Struts, 2.3.29 or 2.5.1." -links "https://struts.apache.org/docs/s2-035"  -sie -u

echo "Importing CVE-2018-1327 (352 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1327 -r https://github.com/apache/struts -e 67ecf3a21608e20449bcb7895b22204b400fecd4  -links "https://cwiki.apache.org/confluence/display/WW/S2-056"  -sie -u

echo "Importing CVE-2017-12196 (353 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12196 -r https://github.com/undertow-io/undertow -e 8804170ce3186bdd83b486959399ec7ac0f59d0f,facb33a5cedaf4b7b96d3840a08210370a806870  -descr "Overview: io.undertow:undertow-core is a Java web server based on non-blocking IO. Affected versions of this package are vulnerable to Man-in-the-Middle (MitM) attacks. When using a Digest authentication, the server does not ensure that value of the URI attribute in the Authorization header matches URI in HTTP request line. An attacker can use this attack vector in order to access desired content on a server. Remediation: Upgrade io.undertow:undertow-core to version 2.0.3 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-IOUNDERTOW-32142,https://bugzilla.redhat.com/show_bug.cgi?id=1503055"  -sie -u

echo "Importing CVE-2015-5171 (354 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5171 -r https://github.com/cloudfoundry/uaa -e 9730cd6a3bbb481ee4e400b51952b537589c469d  -descr "Password change does not expire existing sessions. After a password reset link is requested and a user’s password is then changed, not all existing sessions are logged out automatically. Logging in with the new password doesn’t invalidate the older session either. Deployments enabled for integration via SAML or LDAP are not affected." -links "https://www.cloudfoundry.org/cve-2015-5170-5173/"  -sie -u

echo "Importing CVE-2013-1966 (355 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-1966 -r https://github.com/apache/struts -e 7e6f641ebb142663cbd1653dc49bed725edf7f56  -sie -u

echo "Importing CVE-2014-3625 (356 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3625 -r https://github.com/spring-projects/spring-framework -e 9cef8e3001ddd61c734281a7556efd84b6cc2755,3f68cd633f03370d33c2603a6496e81273782601,9beae9ae4226c45cd428035dae81214439324676  -sie -u

echo "Importing CVE-2015-5258 (357 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5258 -r https://github.com/spring-projects/spring-social -e 5151e1158e1ed51369e7aba9e8092930d28c31d3  -descr "When authorizing an application against an OAuth 2 API provider, Spring Social is vulnerable to a Cross-Site Request Forgery (CSRF) attack. The attack involves a malicious user beginning an OAuth 2 authorization flow using a fake account with an OAuth 2 API provider, but completing it by tricking the victim into visiting the callback request in their browser. As a consequence, the attacker will have access to the victim's account on the vulnerable site by way of the fake provider account." -links "https://pivotal.io/security/cve-2015-5258"  -sie -u

echo "Importing CVE-2018-17197 (358 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17197 -r https://github.com/apache/tika/ -e 0c49c851979163334ea05cbebdd11ff87feba62d  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHETIKA-72870,https://www.securityfocus.com/bid/106293,https://lists.apache.org/thread.html/7c021a4ea2037e52e74628e17e8e0e2acab1f447160edc8be0eae6d3@%3Cdev.tika.apache.org%3E"  -sie -u

echo "Importing CVE-2019-1003000 (359 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003000 -r https://github.com/jenkinsci/jenkins/ -e fa832c58b06556d9d3e0224be28f9c8673f3230b  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003000,https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266"  -sie -u

echo "Importing CVE-2011-2730 (360 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2011-2730 -r https://github.com/spring-projects/spring-framework -e 9772eb8410e37cd0bdec0d1b133218446c778beb,d95cbe23ee462245c5c2482e175f7b2a921b31c:3.0.x,c8649087792d07df209fc75e0f9e2e3284e09fe:3.1.x  -sie -u

echo "Importing CVE-2018-8008 (361 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8008 -r https://github.com/apache/storm/ -e 1117a37b01a1058897a34e11ff5156e465efb69:master,0fc6b522487c061f89e8cdacf09f722d3f20589:1.0.x,efad4cca2d7d461f5f8c08a0d7b51fabeb82d0a:1.2,f61e5daf299d6c37c7ad65744d02556c94a16a4:1.1  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESTORM-32346,https://lists.apache.org/thread.html/613b2fca8bcd0a3b12c0b763ea8f7cf62e422e9f79fce6cfa5b08a58@%3Cdev.storm.apache.org%3E,http://seclists.org/oss-sec/2018/q2/159"  -sie -u

echo "Importing CVE-2015-8103 (362 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-8103 -r https://github.com/jenkinsci/jenkins -e 5bd9b55a2a3249939fd78c501b8959a804c1164b  -descr "Remote code execution vulnerability due to unsafe deserialization in Jenkins remoting (see https://jenkins.io/blog/2015/11/06/mitigating-unauthenticated-remote-code-execution-0-day-in-jenkins-cli/) Jenkins main line users should update to 1.638. Jenkins LTS users should update to 1.625.2." -links "https://jenkins.io/security/advisory/2015-11-11/"  -sie -u

echo "Importing CVE-2014-3576 (363 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3576 -r https://github.com/apache/activemq -e 00921f22ff9a8792d7663ef8fadd4823402a6324  -sie -u

echo "Importing CVE-2017-1000390 (364 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000390 -r https://github.com/jenkinsci/tikal-multijob-plugin/ -e 2424cec7a099fe4392f052a754fadc28de9f8d86,3e6ab85019334a5b2a438264afdebe439cfc82b4  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32192,https://jenkins.io/security/advisory/2017-10-23/"  -sie -u

echo "Importing CVE-2016-4465 (365 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4465 -r https://github.com/apache/struts -e a0fdca138feec2c2e94eb75ca1f8b76678b4d152,eccc31ebce5430f9e91b9684c63eaaf885e603f9  -descr "If an application allows enter an URL field in a form and built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL. Upgrade to Apache Struts version 2.3.29 or 2.5.1." -links "https://struts.apache.org/docs/s2-041"  -sie -u

echo "Importing CVE-2013-7285 (366 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7285 -r https://github.com/x-stream/xstream -e 6344867dce6767af7d0fe34fb393271a6456672d  -descr "XStream can be used for Remote Code Execution. The processed stream at unmarshalling time contains type information to recreate the formerly written objects. XStream creates therefore new instances based on these type information. An attacker can manipulate the processed input stream and replace or inject objects, that can execute arbitrary shell commands. All versions until and including version 1.4.6 are affected, but a workaround exist." -links "http://x-stream.github.io/CVE-2013-7285.html"  -sie -u

echo "Importing CVE-2016-4468 (367 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4468 -r https://github.com/cloudfoundry/uaa -e 215bd349a63edfef15a1aa07a3969c8991e34570,b384a650a122e42d75e8cbb5624d0274a65cd848,6bf1c0ae1abc9aaba957708e0b2dfb6a70aab826  -descr "There is the potential for a SQL injection attack in UAA for authenticated users." -links "https://pivotal.io/security/cve-2016-4468"  -sie -u

echo "Importing AMQP-590 (368 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b AMQP-590 -r https://github.com/spring-projects/spring-amqp -e 4150f107e60cac4a7735fcf7cb4c1889a0cbab6:1.5.x,462dcb6f1f93d54923daffb9729c1c8519576c08  -descr "Deserialization vulnerability. Add Class/Package White List to Deserializing Message Converters. Related to CVE-2016-6194. Fixed in 1.6 M2, 1.5.5 (see https://jira.spring.io/browse/AMQP-590)" -links "https://github.com/spring-projects/spring-amqp/pull/388"  -sie -u

echo "Importing CVE-2016-2173 (369 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2173 -r https://github.com/spring-projects/spring-amqp -e 4150f107e60cac4a7735fcf7cb4c1889a0cbab6c  -descr "The class org.springframework.core.serializer.DefaultDeserializer does not validate the deserialized object against a whitelist. By supplying a crafted serialized object like Chris Frohoff's Commons Collection gadget, remote code execution can be achieved." -links "https://pivotal.io/security/cve-2016-2173"  -sie -u

echo "Importing CVE-2012-0394 (370 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-0394 -r https://github.com/apache/struts -e 9cad25f258bb2629d263f828574d2671366c238d  -sie -u

echo "Importing CVE-2016-6651 (371 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6651 -r https://github.com/cloudfoundry/uaa -e 6ed7dc22beafeaa054713e63125044332729baa:3.4.5,96f702681676d829628a23db171ffa79a32f03af,0ed081c9b515014a21954db0dc03a3ddbb30fac:3.3.0.6,1368817fe4f4899c06089c940830525bc0327ee:2.7.4.x  -descr "A privilege escalation vulnerability has been identified with the /oauth/token endpoint in UAA allowing users to elevate the privileges in the token issued." -links "https://www.cloudfoundry.org/cve-2016-6651/"  -sie -u

echo "Importing CVE-2016-8749 (372 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-8749 -r https://github.com/apache/camel -e c93a87c36aa4d14ad6f7ee1df9507fa2ca1fd91:camel-2.17.x,7567488f844f01d72840f7ab6ca18114a11f20d:camel-2.19,2b0e96117d6f01eba0c18e2ff8df6a438e81972:camel-2.19,d4102512147eca2af21c3b6ed63a67d852f4e66:camel-2.17.x,af3f54de35a90a5a49a4af4622e8bd1011bf5ec:camel-2.19,57d01e2fc8923263df896e9810329ee5b7f9b69:camel-2.16.x,235036d2396ae45b6809b72a1983dee33b5ba32:camel-2.16.x,10f552643d7e4565104d142bbc160db5a30f9f7:camel-2.17.x,881e5099f94316d4a66ffbff0a3e6915829d49d:camel-2.19,ccf149c76bf37adc5977dc626e141a14e60b5ae:camel-2.16.x,5ae9c0dcc4843347cd01ffb58ce5dd0687755a1:camel-2.17.x,02270ab9c90ac0d59b85dbd59fb9c1007eb44a1:camel-2.19  -descr "Apache Camel's Jackson and JacksonXML unmarshalling operation are vulnerable to Remote Code Execution attacks." -links "http://camel.apache.org/security-advisories.data/CVE-2016-8749.txt.asc?version=2&modificationDate=1486565034000&api=v2"  -sie -u

echo "Importing CVE-2018-1000109 (373 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000109 -r https://github.com/jenkinsci/google-play-android-publisher-plugin -e f81b058289caf3332ae40d599a36a3665b1fa13c  -sie -u

echo "Importing CVE-2018-1114 (374 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1114 -r https://github.com/undertow-io/undertow/ -e 882d5884f2614944a0c2ae69bafd9d13bfc5b64:2.0.5,7f22aa0090296eb00280f878e3731bb71d40f9e:1.4.x  -links "https://snyk.io/vuln/SNYK-JAVA-IOUNDERTOW-72304,https://issues.jboss.org/browse/UNDERTOW-1338,https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1114"  -sie -u

echo "Importing AMQ-5751 (375 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b AMQ-5751 -r https://github.com/apache/activemq -e 886e2d4d97555e2f10276616389a5d1f915bad18,a37b43cca82f108a8e3f5c2803a9b50911a60979:5.11.x:5.11.x  -descr "The number of topics/queues that can be created in ActiveMQ setup does not have a 'max destination' option. Each queue also creates a dispatcher thread so having tens of thousands of queues in one go can potentially cause DOS in broker setup. Fixed in 5.12.0" -links "https://issues.apache.org/jira/browse/AMQ-5751"  -sie -u

echo "Importing CVE-2012-0838 (376 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-0838 -r https://github.com/apache/struts -e b4265d369dc29d57a9f2846a85b26598e83f3892,5f54b8d087f5125d96838aafa5f64c2190e6885b  -sie -u

echo "Importing CVE-2018-17192 (377 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17192 -r https://github.com/apache/nifi/ -e dbf259508c2b8e176d8cb837177aaadbf44f0670  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHENIFI-72711,https://issues.apache.org/jira/browse/NIFI-5258,https://nifi.apache.org/security.html#CVE-2018-17192"  -sie -u

echo "Importing CVE-2017-12610 (378 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12610 -r https://github.com/apache/kafka/ -e 9f3468645b968761ca9141d18337cb6adadbae9:0.11.0,47c2753496875db2849065ad91ee03c7c842c8e:master,0b4daa4bf48517b4b3e9cda11692e80ade620b0:0.10.2  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKAFKA-32449,https://lists.apache.org/thread.html/b6157be1a09df332294213bd21e90dcf9fe4c1810193be54620e4210@%3Cusers.kafka.apache.org%3E,https://www.securityfocus.com/bid/104899"  -sie -u

echo "Importing CVE-2013-6372 (379 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6372 -r https://github.com/jenkinsci/subversion-plugin -e 7d4562d6f7e40de04bbe29577b51c79f07d05ba6  -sie -u

echo "Importing CVE-2014-1972 (380 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-1972 -r https://github.com/apache/tapestry-5 -e 95846b173d83c2eb42db75dae3e7d5e13a633946  -sie -u

echo "Importing CVE-2018-17796 (381 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17796 -r https://github.com/wuweiit/mushroom/ -e 8b67e2d88ca8040577248491a5e6e9c806184522  -links "https://snyk.io/vuln/SNYK-JAVA-ORGMARKER-72420,https://github.com/wuweiit/mushroom/issues/16"  -sie -u

echo "Importing CVE-2015-3189 (382 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-3189 -r https://github.com/cloudfoundry/uaa -e a79b89f6e4f66626914b029b7a15a423491f8013  -sie -u

echo "Importing CVE-2017-1000387 (383 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000387 -r https://github.com/jenkinsci/build-publisher-plugin/ -e 7f80f0d7c9cd96a2d660eeb8b695297bef064059,e9c1b263400e42aaa3f9fcbbd0e8b1e85c76e3a0  -links "https://jenkins.io/security/advisory/2017-10-23/,https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32180"  -sie -u

echo "Importing CVE-2019-1003023 (384 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003023 -r https://github.com/jenkinsci/warnings-ng-plugin/ -e 58d4cd85a7fc68ded989b6019c8c0cba3a457d15  -descr "A cross-site scripting vulnerability exists in Jenkins Warnings Next Generation Plugin 1.0.1 and earlier in src/main/java/io/jenkins/plugins/analysis/core/model/DetailsTableModel.java, src/main/java/io/jenkins/plugins/analysis/core/model/SourceDetail.java, src/main/java/io/jenkins/plugins/analysis/core/model/SourcePrinter.java, src/main/java/io/jenkins/plugins/analysis/core/util/Sanitizer.java, src/main/java/io/jenkins/plugins/analysis/warnings/DuplicateCodeScanner.java that allows attackers with the ability to control warnings parser input to have Jenkins render arbitrary HTML." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003023,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1271"  -sie -u

echo "Importing CVE-2015-1427 (385 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1427 -r https://github.com/elastic/elasticsearch -e 4e952b2d75de6ca4caf4b6743462714f3b60d07f:1.4.x,764fda6420a0aa10db4abef15429b5e77b9be8bf,69735b0f4ab9ad7df4b82e8c917589b52cb9978c:1.3.x  -sie -u

echo "Importing CVE-2018-8014 (386 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8014 -r https://github.com/apache/tomcat/ -e d83a76732e6804739b81d8b2056365307637b42d  -links "https://tomcat.apache.org/security-7.html#Fixed_in_Apache_Tomcat_7.0.89,http://svn.apache.org/viewvc?view=revision&revision=1831730,https://lists.apache.org/thread.html/fbfb713e4f8a4c0f81089b89450828011343593800cae3fb629192b1@%3Cannounce.tomcat.apache.org%3E"  -sie -u

echo "Importing CVE-2015-5344 (387 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5344 -r https://github.com/apache/camel -e 4491c080cb6c8659fc05441e49307b7d4349aa56,8386d8f7260143802553bc6dbae2880d6c0bafda  -sie -u

echo "Importing APACHE-AXIS2-5683 (388 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b APACHE-AXIS2-5683 -r https://github.com/apache/axis2-java -e 1b560264151217dae8b34b6aa4dfff4f51377656  -descr "org.apache.axis2:axis2 is a Web Services / SOAP / WSDL engine, the successor to Apache Axis SOAP stack. Affected versions of this package are vulnerable to Cross-Site Scripting (XSS) attacks. When using user input to perform tasks on the server, characters like \< > ' \' must escaped properly. Otherwise, an attacker can manipulate the input to introduce additional attributes, potentially executing code. This may lead to a Cross-Site Scripting (XSS) vulnerability, assuming an attacker can influence the value entered into the template. BUG: Improper Neutralization of Script-Related HTML Tags in a Web Page (Basic XSS) - ListingAgent.java. Remediation: Upgrade axis2 to version 1.7.4 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEAXIS2-31608,https://issues.apache.org/jira/browse/AXIS2-5683,https://svn.apache.org/viewvc?view=revision&revision=1746886"  -sie -u

echo "Importing CVE-2018-1000407 (389 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000407 -r https://github.com/jenkinsci/jenkins/ -e df87e12ddcfeafdba6e0de0e07b3e21f8473ece6  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000407,https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1129"  -sie -u

echo "Importing CVE-2016-4000 (390 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-4000 -r https://github.com/jythontools/jython/ -e 4c337213bd2964bb36cef2d31509b49647ca6f2a  -links "https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=864859,http://www.debian.org/security/2017/dsa-3893,https://hg.python.org/jython/file/v2.7.1rc1/NEWS,https://hg.python.org/jython/rev/d06e29d100c0,https://security-tracker.debian.org/tracker/CVE-2016-4000,https://snyk.io/vuln/SNYK-JAVA-ORGPYTHON-31451,http://bugs.jython.org/issue2454"  -sie -u

echo "Importing CVE-2018-12023 (391 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12023 -r https://github.com/FasterXML/jackson-databind/ -e 7487cf7eb14be2f65a1eb108e8629c07ef45e0a:2.8.11,28badf7ef60ac3e7ef151cd8e8ec010b8479226:2.7.9  -descr "Block polymorphic deserialization of types from Oracle JDBC driver. Description: There is a potential remote code execution (RCE) vulnerability, if user is 1. handling untrusted content (where attacker can craft JSON) 2. using 'Default Typing' feature (or equivalent; polymorphic value with base type of java.lang.Object  3. has oracle JDBC driver jar in classpath  4. allows connections from service to untrusted hosts (where attacker can run an LDAP service). (note: steps 1 and 2 are common steps as explained in https://medium.com/@cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062). To solve the issue, 2 types from JDBC driver are blacklisted to avoid their use as 'serialization gadgets'." -links "https://github.com/FasterXML/jackson/wiki/Jackson-Release-2.8,https://github.com/FasterXML/jackson-databind/issues/2058"  -sie -u

echo "Importing CVE-2018-1258 (392 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1258 -r https://github.com/spring-projects/spring-security/ -e fed15f2b01b763158f6650afa13059203366974:master,7b8fa90d96aaf751a3256fa755d5f17e081c20f:5.0.5  -links "https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORK-31651,https://spring.io/blog/2018/05/09/spring-project-vulnerability-reports-published"  -sie -u

echo "Importing CVE-2018-11784 (393 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11784 -r https://github.com/apache/tomcat/ -e efb860b3ff8ebcf606199b8d0d432f76898040da  -descr "When the default servlet returned a redirect to a directory (e.g. redirecting to /foo/ when the user requested /foo) a specially crafted URL could be used to cause the redirect to be generated to any URI of the attackers choice.This issue was reported to the Apache Tomcat Security Team by Sergey Bobrov on 28 August 2018 and made public on 3 October 2018.Affects: 9.0.0.M1 to 9.0.11Affects: 8.5.0 to 8.5.33Affects: 7.0.23 to 7.0.90" -links "https://tomcat.apache.org/security-7.html,https://tomcat.apache.org/security-8.html,https://tomcat.apache.org/security-9.html"  -sie -u

echo "Importing JAVAMELODY-631 (394 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b JAVAMELODY-631 -r https://github.com/javamelody/javamelody -e dd8816863d8d943f819a3fa797c349236e7546d4  -descr "When using the collector server, minor security issue if XML transport format with xstream is configured in the collector server parameters." -links "https://github.com/javamelody/javamelody/issues/631"  -sie -u

echo "Importing CVE-2017-9096 (395 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9096 -r https://github.com/itext/itext7 -e 930a1c81f8ea4952df540f041befbfa2d6757838  -sie -u

echo "Importing CVE-2016-3674 (396 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3674 -r https://github.com/x-stream/xstream -e 7c77ac0397a1f93c69d2776a13c31957f55d1647,696ec886a23dae880cf12e34e1fe09c5df8fe94:v-1.4.x,5b5cd6d8137f645c5d57b648afb1a305967aa7f:v-1.4.x,c9b121a88664988ccbabd83fa27bfc2a5e0bd139,25c6704bea149ee93c294ae5b6e0aecd182fea88,87172cfc1dd7f8f6e137963c778b03efd14ac446,806949e1b3c22a3b31819a37402489a0303221a:v-1.4.x,e4f1457e681e015be83c6b0b84947676980e29d:v-1.4.x  -sie -u

echo "Importing CVE-2017-13309 (397 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-13309 -r https://github.com/google/conscrypt/ -e e56958e7dea05c1784317f139e2216e2e707d391  -descr "SSLEngine bug with multiple heap buffer inputs. When the SSLEngine overload that accepts an array of ByteBuffers iscalled with heap buffers for both the source and destination, those heap buffers are converted to direct buffers for passing to JNI by way of copying them to a single temporary direct buffer.  A bug in the reading of the encrypted data out of BoringSSL resulted in the data being placed at the wrong offset of the temporary buffer, meaning that the output data was prefixed in the worst case by the plaintext." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-13309,https://github.com/google/conscrypt/pull/485"  -sie -u

echo "Importing CVE-2013-5855 (398 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-5855 -r https://github.com/javaserverfaces/mojarra -e 9827e56928abd657a7e7887f7e82ac9bc8a9c10b,3d476326c7ff32fe17357ac44a7fe194874df246  -sie -u

echo "Importing CVE-2015-6524 (399 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-6524 -r https://github.com/apache/activemq -e 0b5231ada5ce365b41832ba8752ee210145d1cbe  -sie -u

echo "Importing CVE-2018-8016 (400 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8016 -r https://github.com/beobal/cassandra/ -e 28ee665b3c0c9238b61a871064f024d54cddcc79  -descr "CVE-2018-8016 describes an issue with the default configuration of Apache Cassandra releases 3.8 through 3.11.1 which binds an unauthenticated JMX/RMI interface to all network interfaces allowingattackers to execute arbitrary Java code via an RMI request. This issue is a regression of the previously disclosed CVE-2015-0225.The regression was introduced inhttps://issues.apache.org/jira/browse/CASSANDRA-12109.The fix for the regression is implemented inhttps://issues.apache.org/jira/browse/CASSANDRA-14173.This fix is contained in the 3.11.2 release of Apache Cassandra.- The Apache Cassandra PMC" -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-8016,https://issues.apache.org/jira/browse/CASSANDRA-14173"  -sie -u

echo "Importing CVE-2018-1999036 (401 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999036 -r https://github.com/jenkinsci/ssh-agent-plugin/ -e 3a8abe1889d25f9a73cdba202cf27212b273de4d  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32452,https://jenkins.io/security/advisory/2018-07-30/#SECURITY-704"  -sie -u

echo "Importing CVE-2017-4960 (402 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4960 -r https://github.com/cloudfoundry/uaa -e 78731f8aa37a53385d0194821a5356ab66e2138:3.9.8,5eab756eaf4bb397302f00fbd0273f2470009d38  -sie -u

echo "Importing CVE-2016-9879 (403 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-9879 -r https://github.com/spring-projects/spring-security -e 666e356ebc479194ba51e43bb99fc42f849b6175  -sie -u

echo "Importing CVE-2018-1000862 (404 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000862 -r https://github.com/jenkinsci/jenkins/ -e c19cc705688cfffa4fe735e0edbe84862b6c135f  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-72670,https://jenkins.io/security/advisory/2018-12-05/#SECURITY-904"  -sie -u

echo "Importing CVE-2017-7525 (405 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7525 -r https://github.com/FasterXML/jackson-databind -e e8f043d1aac9b82eee907e0f0c3abbdea723a935,60d459cedcf079c6106ae7da2ac562bc32dcabe1,ddfddfba6414adbecaff99684ef66eebd3a92e92  -descr "When configured to enable default typing, Jackson contained a deserialization vulnerability that could lead to arbitrary code execution. Jackson fixed this vulnerability by blacklisting known 'deserialization gadgets'. This solves an incomplete fix for CVE-2017-4995-JK (main description at: https://github.com/FasterXML/jackson-databind/issues/1599 Issues not addressed by the incomplete fix of CVE-2017-4995-JK: https://github.com/FasterXML/jackson-databind/issues/1680 and https://github.com/FasterXML/jackson-databind/issues/1737)" -links "https://github.com/FasterXML/jackson-databind/issues/1723"  -sie -u

echo "Importing CVE-2018-1000632 (406 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000632 -r https://github.com/dom4j/dom4j -e e598eb43d418744c4dbf62f647dd2381c9ce9387  -sie -u

echo "Importing CVE-2018-1335 (407 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1335 -r https://github.com/apache/tika/ -e e82c2efd2b1ac731b6954634741b70ecf0ed6f01,4fdc51a40bf9532d7db57d0b08c1aec3931468ad,302f22aff7a836868b270038e1d66002a2004869,ffb48dd29d0c2009490caefda75e5b57c7958c51,d1bc09386405d28d6b0f0a29ce8c3e7efd72d6c7,5d983aad0b68a228f180686a4135ed8c7cd589f1,b2d3932b847a171a85e356aa230af461a0f80d91  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHETIKA-32232,https://github.com/apache/tika,https://lists.apache.org/thread.html/b3ed4432380af767effd4c6f27665cc7b2686acccbefeb9f55851dca@%3Cdev.tika.apache.org%3E"  -sie -u

echo "Importing CVE-2015-4165 (408 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-4165 -r https://github.com/elastic/elasticsearch -e f5cfb2a1869d1a52930cbd3138278a6e2c1b22e6  -sie -u

echo "Importing CVE-2016-2174 (409 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2174 -r https://github.com/apache/ranger -e da3a3233d5679284142eb2887c91a754a0da70b:master,8618870d1b4acfae4114dd247a362cfa8493ab9:0.5  -sie -u

echo "Importing CVE-2018-17186 (410 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17186 -r https://github.com/apache/syncope/ -e 979c28abf2587c73b57d20e4b892410fdd336f0:2.0.11,a0f35f45f8ca5c98853ae8477fb2db81a84709a:2.1.2,bdb6a180dcae6f1baaff16619cb906b7292da0d:master  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHESYNCOPECLIENT-72569,https://syncope.apache.org/security#CVE-2018-17186:_XXE_on_BPMN_definitions"  -sie -u

echo "Importing CVE-2015-5211 (411 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5211 -r https://github.com/spring-projects/spring-framework -e 2bd1daa75ee0b8ec33608ca6ab065ef3e1815543,03f547eb9868f48f44d59b56067d4ac4740672c3,03f547eb9868f48f44d59b56067d4ac4740672c3:3.2.x,a95c3d820dbc4c3ae752f1b3ee22ee860b162402:4.1.x  -descr "Under some situations, the Spring Framework is vulnerable to a Reflected File Download (RFD) attack. The attack involves a malicious user crafting a URL with a batch script extension that results in the response being downloaded rather than rendered and also includes some input reflected in the response." -links "https://pivotal.io/security/cve-2015-5211"  -sie -u

echo "Importing CVE-2016-1000352 (412 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000352 -r https://github.com/bcgit/bc-java -e 9385b0ebd277724b167fe1d1456e3c112112be1f  -descr "ECIES allows the use of unsafe ECB mode. This algorithm is now removed from the provider." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2017-14949 (413 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-14949 -r https://github.com/restlet/restlet-framework-java -e fe75aff3af23b879b984db7a2b6824cee0ef0fc:2.3,97a8d1d62612683817c785e99c4166bcde8cf1c:2.4  -sie -u

echo "Importing CVE-2013-7397 (414 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7397 -r https://github.com/AsyncHttpClient/async-http-client -e df6ed70e86c8fc340ed75563e016c8baa94d7e72  -sie -u

echo "Importing CVE-2015-7559 (415 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-7559 -r https://github.com/apache/activemq -e b8fc78ec6c367cbe2a40a674eaec64ac3d7d1ec:5.14.x,338a74dfa42a7b19d39adecacfa5f626a050e807  -descr "It was found that Apache ActiveMQ client exposed a remote shutdown command in the ActiveMQConnection class. An attacker could use this flaw to achieve denial of service on a client. Versions Affected: Apache ActiveMQ 5.0.0 - 5.14.4. Mitigation: Upgrade to Apache ActiveMQ 5.14.5. (see https://issues.apache.org/jira/browse/AMQ-6470)" -links "http://activemq.apache.org/security-advisories.data/CVE-2015-7559-announcement.txt"  -sie -u

echo "Importing CVE-2018-1260 (416 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1260 -r https://github.com/spring-projects/spring-security-oauth/ -e adb1e6d19c681f394c9513799b81b527b0cb007:2.3.3,8e9792c1963f1aeea81ca618785eb8d71d1cd1d:2.2.2,6b1791179c1092553aa0690da22dac4dff2fc58:2.1.2,1c6815ac1b26fb2f079adbe283c43a7fd0885f3:2.0.15  -links "https://pivotal.io/security/cve-2018-1260,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKSECURITYOAUTH-31676,http://gosecure.net/2018/05/17/beware-of-the-magic-spell-part-2-cve-2018-1260/"  -sie -u

echo "Importing CVE-2018-8041 (417 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8041 -r https://github.com/apache/camel/ -e a0d25d9582c6ee85e9567fa39413df0b4f02ef7:2.22.1,63c7c080de4d18f9ceb25843508710df2c2c6d4:2.20.4,4580e4d6c65cfd544c1791c824b5819477c583c:master,4f401c09d22c45c94fa97746dc31905e06b19e3:2.21.2  -descr "" -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHECAMEL-72377,https://issues.apache.org/jira/browse/CAMEL-12630,http://camel.apache.org/security-advisories.data/CVE-2018-8041.txt.asc?version=1&modificationDate=1536746339000&api=v2"  -sie -u

echo "Importing CVE-2018-1256 (418 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1256 -r https://github.com/pivotal-cf/spring-cloud-sso-connector/ -e ef647a2acf2363c6018e8543d665ac8862593372  -descr "Issuer validation regression in Spring Cloud SSO Connector. Description: Spring Cloud SSO Connector, version 2.1.2, contains a regression which disables issuer validation in resource servers that are not bound to the SSO service. In PCF deployments with multiple SSO service plans, a remote attacker can authenticate to unbound resource servers which use this version of the SSO Connector with tokens generated from another service plan. Affected Pivotal Products and Versions: Spring Cloud SSO Connector version 2.1.2. Mitigation: Use Spring Cloud SSO Connector: 2.1.3 Or alternatively, you can perform one of the following workarounds: Bind your resource server to the SSO service plan via a service instance binding; Set sso.connector.cloud.available=true within your Spring application properties" -links "https://pivotal.io/security/cve-2018-1256"  -sie -u

echo "Importing CVE-2015-5253 (419 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5253 -r https://github.com/apache/cxf -e 845eccb6484b43ba02875c71e824db23ae4f20c0  -sie -u

echo "Importing CVE-2018-1000548 (420 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000548 -r https://github.com/umlet/umlet/ -e e1c4cc6ae692cc8d1c367460dbf79343e996f9bd  -links "https://snyk.io/vuln/SNYK-JAVA-COMUMLET-32394,https://github.com/umlet/umlet/issues/500"  -sie -u

echo "Importing CVE-2016-3093 (421 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3093 -r https://github.com/jkuhnert/ognl/ -e ae43073fbf38db8371ff4f8bf2a966ee3b5f7e92  -sie -u

echo "Importing CVE-2018-1000129 (422 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000129 -r https://github.com/rhuss/jolokia -e 5895d5c137c335e6b473e9dcb9baf748851bbc5f  -sie -u

echo "Importing CVE-2019-1003026 (423 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003026 -r https://github.com/jenkinsci/mattermost-plugin -e 51ebae2c57977193b45cd60fc70595a0e6df4cb2  -descr "org.jenkins-ci.plugins:mattermost is a mattermost plugin for Jenkins.Affected versions of this package are vulnerable to Cross-Site Request Forgery (CSRF) in MattermostNotifier.java that allows attackers with Overall/Read permission to have Jenkins connect to an attacker-specified Mattermost server and room and send a message.RemediationUpgrade org.jenkins-ci.plugins:mattermost to version 2.6.3 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-173719,https://jenkins.io/security/advisory/2019-02-19/#SECURITY-985"  -sie -u

echo "Importing CVE-2014-0097 (424 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0097 -r https://github.com/spring-projects/spring-security -e 7dbb8e777ece8675f3333a1ef1cb4d6b9be80395:3.2.x,a7005bd74241ac8e2e7b38ae31bc4b0f641ef973,88559882e967085c47a7e1dcbc4dc32c2c796868:3.1.x  -descr "The ActiveDirectoryLdapAuthenticator does not check the password length. If the directory allows anonymous binds then it may incorrectly authenticate a user who supplies an empty password." -links "https://pivotal.io/security/cve-2014-0097"  -sie -u

echo "Importing CVE-2016-1000342 (425 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000342 -r https://github.com/bcgit/bc-java -e 843c2e60f67d71faf81d236f448ebbe56c62c647  -descr "ECDSA does not fully validate ASN.1 encoding of signature on verification. It is possible to inject extra elements in the sequence making up the signature and still have it validate, which in some cases may allow the introduction of invisible data into a signed structure." -links "https://www.bouncycastle.org/releasenotes.html"  -sie -u

echo "Importing CVE-2018-8030 (426 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8030 -r https://github.com/apache/qpid-broker-j/ -e 025b48f3193e2b10b1c41d2bc3bcfc9cfc238a27  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEQPID-32380,https://issues.apache.org/jira/browse/QPID-8203"  -sie -u

echo "Importing CVE-2018-1262 (427 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1262 -r https://github.com/cloudfoundry/uaa/ -e 3633a832885ebf33b2e22cc1c0c8ce605e2c657:4.13.4,dccd3962f969913996ee88f653fce3b108c0205:4.13.4,14c745aa293b8d3ce9cdd6bfbc6c0ef3f269b21:4.12.2,4178762a49f547534b13539ca65e1d370772c38:4.12.2  -links "https://www.cloudfoundry.org/blog/cve-2018-1262/,https://snyk.io/vuln/SNYK-JAVA-ORGCLOUDFOUNDRYIDENTITY-32287"  -sie -u

echo "Importing CVE-2016-6652 (428 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6652 -r https://github.com/spring-projects/spring-data-jpa -e b8e7fecccc7dc8edcabb4704656a7abe6352c08f  -descr "Sort instances handed into user defined Spring Data repository query methods using manually declared JPQL queries are handed to the persistence provider as is and allow attackers to inject arbitrary JPQL into ORDER BY clauses which they might use to draw conclusions about non-exposed fields based on the query result's element order changing depending on the injected JPQL." -links "https://pivotal.io/security/cve-2016-6652"  -sie -u

echo "Importing CVE-2019-3778 (429 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-3778 -r https://github.com/spring-projects/spring-security-oauth/ -e b436f745af2be24924ecc68524fd2582bcdfdc3:2.2.4,97e0b4ab282acbed3588e05be03d5a0c4dbf336:2.3.5,da157a89402eeb2d5d071db3558c3b417bfc3ed:2.0.17,16d39adbc04bb0cdf217226803d05d6956595d8:2.1.4  -descr "Open Redirector in spring-security-oauth2DescriptionSpring Security OAuth, versions 2.3 prior to 2.3.5, and 2.2 prior to 2.2.4, and 2.1 prior to 2.1.4, and 2.0 prior to 2.0.17, and older unsupported versions could be susceptible to an open redirector attack that can leak an authorization code. A malicious user or attacker can craft a request to the authorization endpoint using the authorization code grant type, and specify a manipulated redirection URI via the 'redirect_uri' parameter. This can cause the authorization server to redirect the resource owner user-agent to a URI under the control of the attacker with the leaked authorization code.This vulnerability exposes applications that meet all of the following requirements:Act in the role of an Authorization Server (e.g. @EnableAuthorizationServer)Uses the DefaultRedirectResolver in the AuthorizationEndpointThis vulnerability does not expose applications that:Act in the role of an Authorization Server and uses a different RedirectResolver implementation other than DefaultRedirectResolverAct in the role of a Resource Server only (e.g. @EnableResourceServer)Act in the role of a Client only (e.g. @EnableOAuthClient)Affected Pivotal Products and VersionsSeverity is critical unless otherwise noted.Spring Security OAuth 2.3 to 2.3.4Spring Security OAuth 2.2 to 2.2.3Spring Security OAuth 2.1 to 2.1.3Spring Security OAuth 2.0 to 2.0.16Older unsupported versions are also affectedMitigationUsers of affected versions should apply the following mitigation:2.3.x users should upgrade to 2.3.52.2.x users should upgrade to 2.2.42.1.x users should upgrade to 2.1.42.0.x users should upgrade to 2.0.17Older versions should upgrade to a supported branchThere are no other mitigation steps necessary.For users of Spring Boot 1.5.x and Spring IO Platform Cairo, it is highly recommended to override the spring-security-oauth version to the latest version containing the patch for the CVE. In order to override the version, you need to declare/set the property spring-security-oauth.version.Below are instructions for users of Spring Boot 1.5.x.To override a property using Maven, declare the property in your pom’s <properties> section:<properties> <spring-security-oauth.version>2.0.17.RELEASE</spring-security-oauth.version></properties>To override a property using Gradle, configure the value in your build.gradle script:ext['spring-security-oauth.version'] = '2.0.17.RELEASE'Or in gradle.properties:spring-security-oauth.version=2.0.17.RELEASENOTE: The same instructions apply for users of Spring IO Platform Cairo. However, the version to specify is 2.2.4.RELEASE" -links "https://pivotal.io/security/cve-2019-3778,https://spring.io/blog/2019/02/21/cve-2019-3778-spring-security-oauth-2-3-5-2-2-4-2-1-4-2-0-17-released,https://github.com/spring-projects/spring-security-oauth/issues/1585"  -sie -u

echo "Importing CVE-2018-12540 (430 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12540 -r https://github.com/vert-x3/vertx-web/ -e 98891b1d9e022b467a3e4674aca4d1889849b1d:master,f42b193b15a29b772fc576b2d0f2497e7474a7e:3.5.3  -descr "" -links "
https://snyk.io/vuln/SNYK-JAVA-IOVERTX-72441,https://github.com/vert-x3/vertx-web/issues/970"  -sie -u

echo "Importing CVE-2015-5347 (431 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-5347 -r https://github.com/apache/wicket -e dffba2ce410ec7e917ad350d3528af4df67bc348  -sie -u

echo "Importing CVE-2018-1000056 (432 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000056 -r https://github.com/jenkinsci/junit-plugin/ -e 15f39fc49d9f25bca872badb48e708a8bb815ea7  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32161,https://jenkins.io/security/advisory/2018-02-05/"  -sie -u

echo "Importing CVE-2015-6748 (433 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-6748 -r https://github.com/jhy/jsoup/ -e 4edb78991f8d0bf87dafde5e01ccd8922065c9b2  -sie -u

echo "Importing CVE-2018-20157 (434 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-20157 -r https://github.com/OpenRefine/OpenRefine/ -e 6a0d7d56e4ffb420316ce7849fde881344fbf881  -links "https://snyk.io/vuln/SNYK-JAVA-ORGOPENREFINE-72721,https://github.com/OpenRefine/OpenRefine/issues/1907"  -sie -u

echo "Importing CVE-2019-1003001 (435 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003001 -r https://github.com/jenkinsci/jenkins/ -e fa832c58b06556d9d3e0224be28f9c8673f3230b  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003001,https://jenkins.io/security/advisory/2019-01-08/#SECURITY-1266"  -sie -u

echo "Importing CVE-2016-0785 (436 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0785 -r https://github.com/apache/struts -e 15857a69e7baf3675804495a5954cd0756ac8364  -sie -u

echo "Importing CVE-2016-2162 (437 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2162 -r https://github.com/apache/struts -e fc2179cf1ac9fbfb61e3430fa88b641d87253327  -sie -u

echo "Importing CVE-2017-8038 (438 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8038 -r https://github.com/cloudfoundry-incubator/credhub -e 632951898a2f1474f699094200367fb405397127,46ae8627a6887d0c810905585b40845193b9a9f8  -sie -u

echo "Importing CVE-2017-8045 (439 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-8045 -r https://github.com/spring-projects/spring-amqp -e 296d481f980fcbecbee01244e3644e254470a86:1.7.x,36e55998f6352ba3498be950ccab1d5f4d0ce655,83fe9fdec2c86a57898d56c5e109debd9d5c07d:1.5.x,6e9e00bb5bf0aa88444146db3c2eae138cc7b0a:1.6.x  -descr "In affected versions of Spring AMQP, a org.springframework.amqp.core.Message may be unsafely deserialized when being converted into a string. A malicious payload could be crafted to exploit this and enable a remote code execution attack." -links "https://pivotal.io/security/cve-2017-8045"  -sie -u

echo "Importing CVE-2018-8013 (440 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8013 -r https://github.com/apache/batik/ -e f91125b26a6ca2b7a1195f1842360bed03629839  -links "https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-8013,https://xmlgraphics.apache.org/security.html"  -sie -u

echo "Importing CVE-2018-11762 (441 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11762 -r https://github.com/apache/tika/ -e a09d853dbed712f644e274b497cce254f3189d57  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHETIKA-72393,https://lists.apache.org/thread.html/ab2e1af38975f5fc462ba89b517971ef892ec3d06bee12ea2258895b@%3Cdev.tika.apache.org%3E"  -sie -u

echo "Importing CVE-2014-3527 (442 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3527 -r https://github.com/spring-projects/spring-security -e 2cb99f079152ac05cee5c90457c7feb3bb2de55:3_2,934937d9c1dc20c396b96c08310b72cfa627acb:3_1  -sie -u

echo "Importing CVE-2013-2251 (443 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2251 -r https://github.com/apache/struts -e 3cfe34fefedcf0fdcfcb061c0aea34a715b7de6:STRUTS_2_3_15_X,630e1ba065a8215c4e9ac03bfb09be9d655c2b6e  -sie -u

echo "Importing CVE-2015-0201 (444 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0201 -r https://github.com/spring-projects/spring-framework -e dc5b5ca8ee09c890352f89b2dae58bc0132d6545,d63cfc8eebc396be009e733a81ebb4c984811f6e  -sie -u

echo "Importing CVE-2018-1000865 (445 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000865 -r https://github.com/jenkinsci/groovy-sandbox/ -e 0cd7ec12b7c56cfa3167d99c5f43147ce05449d3  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000865,https://jenkins.io/security/advisory/2018-10-29/#SECURITY-1186,https://snyk.io/vuln/SNYK-JAVA-ORGKOHSUKE-72667"  -sie -u

echo "Importing SPR-7779 (446 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b SPR-7779 -r https://github.com/spring-projects/spring-framework -e f4a2282d9d9f6e58029022c58311a1db07f7defc  -descr "In versions before 3.0.6 and 3.1 M1, LocaleChangeInterceptor does not validate locale values which may lead to XSS vulnerability" -links "https://jira.spring.io/browse/SPR-7779"  -sie -u

echo "Importing CVE-2017-1000498 (447 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000498 -r https://github.com/BigBadaboom/androidsvg -e 44e4fbf1d0f6db295df34601972741d4cf706cbd  -sie -u

echo "Importing CVE-2011-4461-JETTY (448 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2011-4461-JETTY -r https://github.com/eclipse/jetty.project -e d0b81a185c260ffceecb9d7470b3ddfbfeda4c11,979d6dbbf9416b1a0ad965e2b8a3b11a2d208627  -descr "Jetty 8.1.0.RC2 and earlier computes hash values for form parameters without restricting the ability to trigger hash collisions predictably, which allows remote attackers to cause a denial of service (CPU consumption) by sending many crafted parameters. (see https://bugs.eclipse.org/bugs/show_bug.cgi?id=367638)" -links "https://nvd.nist.gov/vuln/detail/CVE-2011-4461"  -sie -u

echo "Importing SONARQUBE-001 (449 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b SONARQUBE-001 -r https://github.com/SonarSource/sonarqube/ -e 08438a2c47112f2fce1e512f6c843c908abed4c7  -descr "Overvieworg.sonarsource.sonarqube:sonar-plugin-api provides the capability to not only show health of an application but also to highlight issues newly introduced. Affected versions of the package are vulnerable to Arbitrary File Write via Archive Extraction (AKA 'Zip Slip').RemediationUpgrade org.sonarsource.sonarqube:sonar-plugin-api to version 6.7.4 or higher." -links "https://snyk.io/research/zip-slip-vulnerability,https://snyk.io/vuln/SNYK-JAVA-ORGSONARSOURCESONARQUBE-72656"  -sie -u

echo "Importing CVE-2013-4310 (450 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4310 -r https://github.com/apache/struts -e 0c8366cb792227d484b9ca13e537037dd0cb57dc  -sie -u

echo "Importing CVE-2018-8034 (451 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-8034 -r https://github.com/apache/tomcat/ -e 2835bb4e030c1c741ed0847bb3b9c3822e4fbc8a  -descr "host name verification missing in WebSocket client" -links "https://tomcat.apache.org/security-9.html"  -sie -u

echo "Importing CVE-2017-3164 (452 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-3164 -r https://github.com/apache/lucene-solr/ -e e9db95831b9db69fbc0bef499b0d3f41bc6448f:8.x,8b54b20fc488ae3e83f4a350a707dc0303ade23:master,6d63958821232699f0a8423d9b21d4915bfba64:7.x  -descr "SSRF issue in Apache Solr.Versions Affected:Apache Solr versions from 1.3 to 7.6.0Description:The 'shards' parameter does not have a corresponding whitelist mechanism,so it can request any URL.Mitigation:Upgrade to Apache Solr 7.7.0 or later.Ensure your network settings are configured so that only trusted traffic isallowed to ingress/egress your hosts running Solr." -links "https://wiki.apache.org/solr/SolrSecurity,https://issues.apache.org/jira/browse/SOLR-12770,http://mail-archives.apache.org/mod_mbox/www-announce/201902.mbox/%3CCAECwjAVjBN%3DwO5rYs6ktAX-5%3D-f5JDFwbbTSM2TTjEbGO5jKKA%40mail.gmail.com%3E"  -sie -u

echo "Importing PT-2013-65 (453 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b PT-2013-65 -r https://github.com/eclipse/jetty.project -e 458e511ce2f2b47fd216f68c0e385fc06a5f1d2f,0fac295cd82b59085d4aae5ca6792b2cda752455  -descr "The system does not consider that NTFS allows users to address files with extended syntax, while matching the requested resource URL with locations defined in web server configuration. This vulnerability allows attackers to obtain JSP script source code and to bypass access restrictions set for certain resources. Fixed in 7.6.14, 8.1.14, 9.0.6, 9.1.0. (see https://bugs.eclipse.org/bugs/show_bug.cgi?id=418014)" -links "http://en.securitylab.ru/lab/PT-2013-65"  -sie -u

echo "Importing CVE-2014-8122 (454 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-8122 -r https://github.com/weld/core -e 8e413202fa1af08c09c580f444e4fd16874f9c65,29fd1107fd30579ad9bb23fae4dc3ba464205745,6808b11cd6d97c71a2eed754ed4f955acd789086  -sie -u

echo "Importing CVE-2015-3253 (455 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-3253 -r https://github.com/apache/groovy -e 09e9778e8a33052d8c27105aee5310649637233d  -sie -u

echo "Importing CVE-2013-7315 (456 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-7315 -r https://github.com/spring-projects/spring-framework -e 7576274874deeccb6da6b09a8d5bd62e8b5538b7  -sie -u

echo "Importing CVE-2018-1000850 (457 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000850 -r https://github.com/square/retrofit/ -e b9a7f6ad72073ddd40254c0058710e87a073047d  -links "https://snyk.io/vuln/SNYK-JAVA-COMSQUAREUPRETROFIT2-72720,https://ihacktoprotect.com/post/retrofit-path-traversal/"  -sie -u

echo "Importing CVE-2013-4316 (458 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4316 -r https://github.com/apache/struts -e 58947c3f85ae641c1a476316a2888e53605948d1  -sie -u

echo "Importing CVE-2012-0392 (459 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-0392 -r https://github.com/apache/struts -e 34c80dae734e70f13c0e46f9c83602fb71318e58  -sie -u

echo "Importing CVE-2017-1000243 (460 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000243 -r https://github.com/jenkinsci/favorite-plugin/ -e b6359532fe085d9ea6b7894e997e797806480777  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32197,https://jenkins.io/security/advisory/2017-06-06/"  -sie -u

echo "Importing CVE-2018-11758 (461 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11758 -r https://github.com/apache/cayenne -e 6fc896b65ed871be33dcf453cde924bf73cf83db  -sie -u

echo "Importing 413684 (462 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b 413684 -r https://github.com/eclipse/jetty.project -e 2f08ba29487aff6624dbf947b1fbd845cdd33464  -descr "As Jetty is delivered, adding a trailing slash to a JSP page causes it to be served as a raw source file. This vulnerability affects releases >=7.6.9 <9.0.5. Please update to|7.6.13,8.1.13,9.0.5" -links "https://bugs.eclipse.org/bugs/show_bug.cgi?id=413684"  -sie -u

echo "Importing CVE-2018-1000009 (463 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000009 -r https://github.com/jenkinsci/checkstyle-plugin/ -e 365d6164ebce7b65ae010c71016924ef8b98c1a0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32169,https://jenkins.io/security/advisory/2018-01-22/"  -sie -u

echo "Importing CVE-2019-1003003 (464 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003003 -r https://github.com/jenkinsci/jenkins/ -e 07c09bebb8396a48063c1da4fc4b628acddd72a8  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003003,https://jenkins.io/security/advisory/2019-01-16/#SECURITY-868"  -sie -u

echo "Importing CVE-2018-17297 (465 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-17297 -r https://github.com/looly/hutool/ -e 8d7d0b7fb5ea4f7447b40131bffc1ec506a6528e,fed1a1f747a9308e2f65f8dbbff05ce62478ecc0,9f8a801c7b98b75ee681c0988e1a58bcfdc21756  -links "https://snyk.io/vuln/SNYK-JAVA-CNHUTOOL-72401,https://github.com/looly/hutool/issues/162"  -sie -u

echo "Importing CVE-2018-12542 (466 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12542 -r https://github.com/vert-x3/vertx-web/ -e 57a65dce6f4c5aa5e3ce7288685e7f3447eb8f3b  -links "https://snyk.io/vuln/SNYK-JAVA-IOVERTX-72442,https://github.com/vert-x3/vertx-web/issues/1025,https://bugs.eclipse.org/bugs/show_bug.cgi?id=539171"  -sie -u

echo "Importing CVE-2017-17485 (467 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-17485 -r https://github.com/FasterXML/jackson-databind/ -e 2235894210c75f624a3d0cd60bfb0434a20a18bf  -links "https://github.com/FasterXML/jackson-databind/issues/1855"  -sie -u

echo "Importing CVE-2017-9803 (468 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9803 -r https://github.com/apache/lucene-solr -e b091934f9e98568b848d0584a1145c8e514cbd21  -sie -u

echo "Importing CVE-2018-1271 (469 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1271 -r https://github.com/spring-projects/spring-framework/ -e 0e28bee0f155b9bf240b4bafc4646e4810cb23f:5.0.5,98ad23bef8e2e04143f8f5b201380543a8d8c0c:5.0.5,f59ea610dfcf55cd0b42f6dd76a9b3dab0218aa:5.0.5,695bf2961feffd35b5560ccc982a2189dcca611:5.05,91b803a2310344d925e5d4b1709bbcea9037554:5.0.5,13356a7ee2240f740737c5c83bdccdacc30603a:5.0.5,b9ebdaaf3710db473a2e1fec8641c316483a22a:4.3.x  -links "https://www.securityfocus.com/bid/103699,https://pivotal.io/security/cve-2018-1271"  -sie -u

echo "Importing CVE-2010-3260 (470 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2010-3260 -r https://github.com/orbeon/orbeon-forms -e aba6681660f65af7f1676434da68c10298c30200  -sie -u

echo "Importing CVE-2014-0116 (471 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-0116 -r https://github.com/apache/struts -e 74e26830d2849a84729b33497f729e0f033dc147  -descr "Fix for ue CVE-2014-0094, CVE-2014-0112, CVE-2014-0113 and CVE-2014-0116" -links "https://github.com/apache/struts/pull/70"  -sie -u

echo "Importing CVE-2017-3159 (472 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-3159 -r https://github.com/apache/camel -e dcb5a74a3987d2264ad195c7844bbb6c81216610,6b979d07fd4be6ac913368f2abeae690d3325d37,20e26226107f3133c87d0f5c845e02f824823f69  -sie -u

echo "Importing CVE-2016-1000343 (473 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-1000343 -r https://github.com/bcgit/bc-java/ -e 50a53068c094d6cff37659da33c9b4505becd389  -links "https://snyk.io/vuln/SNYK-JAVA-ORGBOUNCYCASTLE-32361"  -sie -u

echo "Importing CVE-2016-7051 (474 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-7051 -r https://github.com/FasterXML/jackson-dataformat-xml -e eeff2c312e9d4caa8c9f27b8f740c7529d00524a  -sie -u

echo "Importing CVE-2018-1000104 (475 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000104 -r https://github.com/jenkinsci/coverity-plugin/ -e 34b7c2b07014b8e1e708361170146600db172491  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32158,https://jenkins.io/security/advisory/2018-02-26/#SECURITY-260"  -sie -u

echo "Importing CVE-2013-4221 (476 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-4221 -r https://github.com/restlet/restlet-framework-java/ -e 12cc79b3953c7bd276e9f1cae2fbfdb9c1a6f07:2.4,b85c2ef182c69c5e2e21df008ccb249ccf80c7b:2.1,c3015e4783c2a36e7528aa611c911b7d8c4ec5b:2.0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGRESTLET-72458,https://github.com/restlet/restlet-framework-java/issues/774,http://blog.diniscruz.com/2013/08/using-xmldecoder-to-execute-server-side.html"  -sie -u

echo "Importing CVE-2015-1830 (477 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1830 -r https://github.com/apache/activemq -e 729c4731574ffffaf58ebefdbaeb3bd19ed1c7b7,9fd5cb7dfe0fcc431f99d5e14206e0090e72f36b  -sie -u

echo "Importing CVE-2016-2192 (478 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2192 -r https://github.com/tada/pljava -e f0a41359ede67335c5ef3fe73a9f10da96d71760  -sie -u

echo "Importing CVE-2018-1000406 (479 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000406 -r https://github.com/jenkinsci/jenkins/ -e c3351d2e7c3edfee82b9470e9aa1168982296072  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000406,https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1074"  -sie -u

echo "Importing CVE-2016-6637 (480 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6637 -r https://github.com/cloudfoundry/uaa -e 703542183b14b3ef1e04d68d83484d9eaaeb2f0:2.7.4.x,32569285018a464dcbd9d4c120a11cc4b767f8e:3.3.0.x,f3d8a9e1ee1acac5bf1f8487ac9461f4cf4505c:3.4.x  -descr "The profile and authorize approval pages do not contain CSRF tokens, making an exploit to approve or deny scopes possible." -links "https://www.cloudfoundry.org/cve-2016-6637/"  -sie -u

echo "Importing CVE-2018-11771 (481 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11771 -r https://github.com/apache/commons-compress -e a41ce6892cb0590b2e658704434ac0dbcb6834c8  -sie -u

echo "Importing CVE-2017-7672 (482 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7672 -r https://github.com/apache/struts -e 931df54ab379bf4eb5a625bf05066b8563c3737b  -descr "Possible DoS attack when using URLValidator (similar to S2-044). If an application allows enter an URL in a form field and built-in URLValidator is used, it is possible to prepare a special URL which will be used to overload server process when performing validation of the URL. Solution: upgrade to Apache Struts version 2.5.12. This is also known as S2-047" -links "https://cwiki.apache.org/confluence/display/WW/S2-047"  -sie -u

echo "Importing CVE-2018-5968 (483 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-5968 -r https://github.com/FasterXML/jackson-databind/ -e 038b471e2efde2e8f96b4e0be958d3e5a1ff1d0:2.8.11.1  -links "https://github.com/FasterXML/jackson-databind/issues/1899,https://snyk.io/vuln/SNYK-JAVA-COMFASTERXMLJACKSONCORE-32044"  -sie -u

echo "Importing CVE-2017-1000503 (484 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000503 -r https://github.com/jenkinsci/jenkins/ -e ccc374a7176d7704941fb494589790b7673efe2:master,9b39411b1ae07ce8bf6c7df457bde1c6dabba9f:2.95,eec0188cc45d75fd519a5d831b54781ac801dac:2.89.2  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32173,https://jenkins.io/security/advisory/2017-12-14/"  -sie -u

echo "Importing CVE-2018-1261 (485 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1261 -r https://github.com/spring-projects/spring-integration-extensions/ -e a5573eb232ff85199ff9bb28993df715d9a19a25  -links "https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKINTEGRATION-31675,https://pivotal.io/security/cve-2018-1261"  -sie -u

echo "Importing CVE-2017-5656 (486 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5656 -r https://github.com/apache/cxf -e 66c2c5b9  -sie -u

echo "Importing CVE-2018-15801 (487 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-15801 -r https://github.com/spring-projects/spring-security -e c70b65c5df0e170a2d34d812b83db0b7bc71ea25  -links "https://pivotal.io/security/cve-2018-15801,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKSECURITY-72709,https://github.com/spring-projects/spring-security/issues/6073"  -sie -u

echo "Importing CVE-2017-4992 (488 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4992 -r https://github.com/cloudfoundry/uaa -e 96a294013c0c9a13ef32afc49d2b759f5107dc4:2.7.4.x,1c9c6dd88266cfa7d333e5d8be1031fa31c5c93:3.9.x,3ce42a4c75828cb58287c3c7495dde3f5261f12:3.6.x,4f942064d85454a4bcc4da04cd482d114816c14a  -descr "It is possible to perform a RCE attack with a malicious Content-Type value. If the Content-Type value isn't valid an exception is thrown which is then used to display an error message to a user." -links "https://www.cloudfoundry.org/cve-2017-4992/"  -sie -u

echo "Importing CVE-2018-1000873 (489 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000873 -r https://github.com/FasterXML/jackson-modules-java8/ -e 7de5c8dcd7e2f59f4f5a0c6c9b92cc9e785f9eac,ba27ce5909dfb49bcaf753ad3e04ecb980010b0b  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000873,https://bugzilla.redhat.com/show_bug.cgi?id=1665601,https://github.com/FasterXML/jackson-modules-java8/issues/90"  -sie -u

echo "Importing CVE-2017-13098 (490 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-13098 -r https://github.com/bcgit/bc-java/ -e a00b684465b38d722ca9a3543b8af8568e6bad5c  -sie -u

echo "Importing CVE-2018-1000408 (491 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000408 -r https://github.com/jenkinsci/jenkins/ -e 01157a699f611ca7492e872103ac01526a982cf2  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-1000408,https://jenkins.io/security/advisory/2018-10-10/#SECURITY-1128"  -sie -u

echo "Importing CVE-2018-1000054 (492 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000054 -r https://github.com/jenkinsci/ccm-plugin/ -e 066cb43b4413b3490d822ec8b8a32072ebd213ca  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32163,https://jenkins.io/security/advisory/2018-02-05/"  -sie -u

echo "Importing CVE-2013-5679 (493 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-5679 -r https://github.com/ESAPI/esapi-java-legacy -e 41138fef5f63d9cf0d5e05d2bee2c7f682ffef3f  -sie -u

echo "Importing HUDSON-483532 (494 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HUDSON-483532 -r https://git.eclipse.org/r/hudson/org.eclipse.hudson.core -e 6cae5b7f9f88ac0afdc13ae8ea1c2f5070441b9e  -descr "The use of the Hudson Command line Interface is now disabled by default and we recommend that it not be re-enabled unless Hudson is running inside of a controlled environment. An option is available on the main Hudson settings screen to explicitly enable the CLI should it be required. Update to 3.3.3" -links "https://bugs.eclipse.org/bugs/show_bug.cgi?id=483532"  -sie -u

echo "Importing CVE-2017-15719 (495 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-15719 -r https://github.com/sebfz1/wicket-jquery-ui -e 6f33727a1b4aa27d58d672a96154d9061db43fa:6.28.1,82d81bf704bef90b42f62aecbcc7e8c460814b6:8.0.0-M8.1,8aebe1e49a71f10cdd6a073fd09d0d8d82352a0:7.9.2,936c12a2db262cf471c781f0d3c0d0ad61c35c7:8.0.0-M8.1,fa0ce80f8e92c28c801773ed7c28621ae98e872:6.28.1,42294cc890536459b13cf16844cd65cccf66578:8.0.0-M8.1,3e8cfdcb0f8e6e0cf0da01e74501afb5c9bff0f:6.28.1,cc75fdc3e610985a5f391789d33fb70c8c9114d:7.9.2,9f082950a276c8948a4078c2438e284a948ba15:7.9.2  -sie -u

echo "Importing CVE-2017-4995 (496 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-4995 -r https://github.com/spring-projects/spring-security -e 947d11f433b78294942cb5ea56e8aa5c3a0ca43:4.2.x,5dee8534cd1b92952d10cc56335b5d5856f48f3b  -descr "Spring Security configures Jackson with global default typing enabled which means it inherits a Jackson deserialization vulnerability that could lead to arbitrary code execution. (see https://github.com/spring-projects/spring-security/issues/4370)" -links "https://pivotal.io/security/cve-2017-4995"  -sie -u

echo "Importing CVE-2012-6092 (497 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2012-6092 -r https://github.com/apache/activemq -e 51eb87a84be88d28383ea48f6e341ffe1203c5ba  -sie -u

echo "Importing CVE-2019-1003013 (498 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003013 -r https://github.com/jenkinsci/blueocean-plugin/ -e 62775e78532b756826bb237775b64a5052624b57  -descr "An cross-site scripting vulnerability exists in Jenkins Blue Ocean Plugins 1.10.1 and earlier in blueocean-commons/src/main/java/io/jenkins/blueocean/commons/stapler/Export.java, blueocean-commons/src/main/java/io/jenkins/blueocean/commons/stapler/export/ExportConfig.java, blueocean-commons/src/main/java/io/jenkins/blueocean/commons/stapler/export/JSONDataWriter.java, blueocean-rest-impl/src/main/java/io/jenkins/blueocean/service/embedded/UserStatePreloader.java, blueocean-web/src/main/resources/io/jenkins/blueocean/PageStatePreloadDecorator/header.jelly that allows attackers with permission to edit a user's description in Jenkins to have Blue Ocean render arbitrary HTML when using it as that user." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003013,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-1204"  -sie -u

echo "Importing CVE-2019-7722 (499 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-7722 -r https://github.com/pmd/pmd/ -e e295711343cc155cb64ea0ae29ce9d69201469b3  -descr "PMD 5.8.1 and earlier processes XML external entities in ruleset files it parses as part of the analysis process, allowing attackers tampering it (either by direct modification or MITM attacks when using remote rulesets) to perform information disclosure, denial of service, or request forgery attacks. (PMD 6.x is unaffected because of a 2017-09-15 change.)" -links "https://snyk.io/vuln/SNYK-JAVA-NETSOURCEFORGEPMD-173681,https://github.com/pmd/pmd/issues/1650,https://github.com/pmd/pmd/pull/592"  -sie -u

echo "Importing CVE-2017-3156 (500 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-3156 -r https://github.com/apache/cxf -e 1338469:3.0.x,555843f:3.1.x,e66ce235  -sie -u

echo "Importing CVE-2014-4172 (501 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-4172 -r https://github.com/apereo/java-cas-client -e ab6cbdc3daa451b4fef89c0bd0f4e6568f3aa9ef,ae37092100c8eaec610dab6d83e5e05a8ee58814  -descr "It was found that URL encoding used in the back-channel ticket validation of the JA-SIG CAS client was improper. A remote attacker could exploit this flaw to bypass security constraints by injecting URL parameters. Fixed In Version:	3.1.13, 3.2.2, 3.3.2 (see https://github.com/apereo/java-cas-client/pull/73)" -links "https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2014-4172"  -sie -u

echo "Importing CVE-2016-6812 (502 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6812 -r https://github.com/apache/cxf -e 1f824d80:3.1.x:3.1.x,32e89366:3.1.x:3.1.x,1be97cb1:3.0.x:3.0.x,a30397b0:3.0.x:3.0.x,a23c615b,45b1b5b9  -descr " XSS risk in Apache CXF FormattedServiceListWriter when a request URL contains matrix parameters. This vulnerability affects all versions of Apache CXF prior to 3.0.12, 3.1.9. CXF 3.0.x users should upgrade to 3.0.12 or later as soon as possible. CXF 3.1.x users should upgrade to 3.1.9 or later as soon as possible." -links "http://cxf.apache.org/security-advisories.data/CVE-2016-6812.txt.asc"  -sie -u

echo "Importing HDFS-10276 (503 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HDFS-10276 -r https://github.com/apache/hadoop/ -e 3e4c7906c2cf5c3e4c708fc56b670fa788e8cec:2.8,5ea6fd85c7aff6df28b87789f607bb57ee92063:3.1,e6c162a39466755d35abed7faf2e00d28166553:2.7,2dfaedeb4390569af2036a6e4bd8fcc18506de8:2.9  -descr "HDFS should not expose path info that user has no permission to see. Overview: http://hadoop.apache.org/ is the primary distributed storage used by Hadoop applications. Affected versions of this package are vulnerable to Information Exposure. An attacker may retrieve information about paths that they do not have permissions to see. Remediation: Upgrade org.apache.hadoop:hadoop-hdfs to versions 2.7.4 or higher (Fixed Version/s: 2.8.0, 2.7.4, 3.0.0-alpha1)." -links "https://issues.apache.org/jira/browse/HDFS-10276,https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEHADOOP-32124"  -sie -u

echo "Importing CVE-2018-11799 (504 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-11799 -r https://github.com/apache/oozie/ -e d50df341432df1049c6c85bf2dcda9eb0be04d73  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEOOZIE-72718,https://lists.apache.org/thread.html/347e7a8cb86014b7ca37e49eb00b8d088203bdc0bcfb4799f8e5955a@%3Cuser.oozie.apache.org%3E"  -sie -u

echo "Importing GEODE-4270 (505 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b GEODE-4270 -r https://github.com/apache/geode -e 80ad2d70435fb255a8a2d08c8866fbb30a7bedd3  -descr "GEODE-4270: remove race condition where CacheClientProxy could be asked to authorize a message prior to receiving its security subject. Affected versions of this package are vulnerable to Authentication Bypass. The CacheClientProxy could be asked to authorize a message prior to receiving its security subject. Remediation: Upgrade org.apache.geode:geode-core to version 1.4.0 or higher." -links "https://issues.apache.org/jira/browse/GEODE-4270"  -sie -u

echo "Importing CVE-2018-1275 (506 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1275 -r https://github.com/spring-projects/spring-framework/ -e d3acf45ea4db51fa5c4cbd0bc0e7b6d9ef805e6:4.x,1db7e02de3eb0c011ee6681f5a12eb9d166fea8:5.x  -descr "Spring Framework, versions 5.0.x prior to 5.0.5 and versions 4.3.x prior to 4.3.16, as well as older unsupported versions allow applications to expose STOMP over WebSocket endpoints with a simple, in-memory STOMP broker through the spring-messaging module. A malicious user (or attacker) can craft a message to the broker that can lead to a remote code execution attack. Affected : Spring Framework 5.0 to 5.0.4, Spring Framework 4.3 to 4.3.15, Older unsupported versions are also affected" -links "https://pivotal.io/security/cve-2018-1275"  -sie -u

echo "Importing CVE-2019-1003027 (507 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003027 -r https://github.com/jenkinsci/octopusdeploy-plugin/ -e 40e04160ac77190a51c8e2c3164a0151441efdf4  -descr "SSRF vulnerability due to missing permission check in OctopusDeploy PluginA missing permission check in a form validation method in OctopusDeploy Plugin allowed users with Overall/Read permission to initiate a connection test, sending an HTTP HEAD request to an attacker-specified URL, returning HTTP response code if successful, or exception error message otherwise.Additionally, this form validation method did not require POST requests, resulting in a CSRF vulnerability.This form validation method now requires POST requests and performs a permission check.Affected Versions OctopusDeploy Plugin up to and including 1.8.1Fix OctopusDeploy Plugin should be updated to version 1.9.0" -links "https://snyk.io/vuln/SNYK-JAVA-HUDSONPLUGINSOCTOPUSDEPLOY-173717,https://jenkins.io/security/advisory/2019-02-19/#SECURITY-817"  -sie -u

echo "Importing CVE-2013-2193 (508 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-2193 -r https://github.com/apache/hbase -e 408eb243ad51bbad593d83ad2cfd35cc0e90b38e  -sie -u

echo "Importing CVE-2017-12631 (509 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-12631 -r https://github.com/apache/cxf-fediz -e e7127129dbc0f4ee83985052085e185e750cebbf,ccdb12b26ff89e0a998a333e84dd84bd713ac76:1.4.x-fixes,48dd9b68d67c6b729376c1ce8886f52a57df6c4:1.3.x-fixes  -sie -u

echo "Importing CVE-2013-1880 (510 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-1880 -r https://github.com/apache/activemq -e fafd12dfd4f71336f8e32c090d40ed1445959b40  -sie -u

echo "Importing CVE-2017-7957 (511 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-7957 -r https://github.com/x-stream/xstream -e 8542d02d9ac5d384c85f4b33d6c1888c53bd55d:v-1.4.x,6e546ec366419158b1e393211be6d78ab9604ab:v-1.4.x,b3570be2f39234e61f99f9a20640756ea71b1b4:master  -sie -u

echo "Importing CVE-2017-5644 (512 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5644 -r https://github.com/apache/poi -e 3a328aa220f6979f9805f658ae33244d153beaa7  -sie -u

echo "Importing CVE-2014-3579 (513 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2014-3579 -r https://github.com/apache/activemq-apollo -e e5647554e6801a522c508a8eb457979a9af8c398  -descr "It is possible for a consumer dequeuing XML message(s) to specify an XPath based selector thus causing the broker to evaluate the expression and attempt to match it against the messages in the queue while also performing an XML external entity resolution. Upgrade to Apache ActiveMQ Apollo 1.7.1 (see https://issues.apache.org/jira/browse/APLO-366)" -links "http://activemq.apache.org/security-advisories.data/CVE-2014-3579-announcement.txt"  -sie -u

echo "Importing CVE-2018-12538 (514 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-12538 -r https://github.com/eclipse/jetty.project/ -e a0b8321ef452dddff9bc6c14e3ac0108239bfa2c  -links "https://snyk.io/vuln/SNYK-JAVA-ORGECLIPSEJETTY-32381,https://bugs.eclipse.org/bugs/show_bug.cgi?id=536018,https://github.com/eclipse/jetty.project/issues/2038,https://github.com/CVEProject/cvelist/pull/637"  -sie -u

echo "Importing CVE-2017-5929 (515 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5929 -r https://github.com/qos-ch/logback -e f46044b805bca91efe5fd6afe52257cd02f775f8  -sie -u

echo "Importing CVE-2016-3084 (516 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-3084 -r https://github.com/cloudfoundry/uaa -e 460627ed419e4227b10ff121248b3ffc009011a9,b3834364ab573e9655348193780a56a602fe87b7,14350228989e2aee900b8d48a848293bb5152b6f,66132926f1bac0b878da5841be2f93fa5075d88f  -descr "The UAA reset password flow is vulnerable to a brute force attack due to multiple active codes at a given time. This vulnerability is applicable only when using the UAA internal user store for authentication. Deployments enabled for integration via SAML or LDAP are not affected." -links "https://www.cloudfoundry.org/cve-2016-3084/"  -sie -u

echo "Importing CVE-2016-5641 (517 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-5641 -r https://github.com/swagger-api/swagger-codegen -e 90857e898884238d61dbfbd3ede5c7cc57de483f,cb53ea114ace2e0346a96c00d9403b990a6d4f5f,37e1de6d725bf5c3b9c7464f6ddc4a097513a112,07a852fe78ae71261f617200459e2cdf6529068f,a71c0726099daf8e7b5fe8ed1cef1ec2e03b57c7,56b2b4f2ebecf788fb30d385b3a91e8e1a72296d,cee45bc9aa0296b35170cb10b5132491c5dbdc88,c5724a46d6cbbed03d292a361b3a0d07d1a64dae,9ee10e23977b39f4ad21445316f07271b01e02f1  -descr "Maliciously crafted Swagger documents can be used to dynamically create HTTP API clients and servers with embedded arbitrary code execution in the underlying operating system. This is achieved by the fact that some parsers/generators trust insufficiently sanitized parameters within a Swagger document to generate a client code base. " -links "https://community.rapid7.com/community/infosec/blog/2016/06/23/r7-2016-06-remote-code-execution-via-swagger-parameter-injection-cve-2016-5641"  -sie -u

echo "Importing CVE-2017-1000502 (518 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000502 -r https://github.com/jenkinsci/ec2-plugin/ -e 180f7d0eae6031d67259a5d86d9d7d382f9eb05b  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIPLUGINS-32174,https://jenkins.io/security/advisory/2017-12-06/"  -sie -u

echo "Importing CVE-2015-0886 (519 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-0886 -r https://github.com/djmdjm/jBCrypt -e 0c28b698e79b132391be8333107040d774c79995  -sie -u

echo "Importing CVE-2018-1999045 (520 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999045 -r https://github.com/jenkinsci/jenkins -e ef9583a24abc4de157e1570cb32d7a273d327f36  -sie -u

echo "Importing CVE-2017-15691 (521 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-15691 -r https://github.com/apache/uima-uimaj/ -e 39909bf21fd694f4fb792d1de8adc72562ead25e  -links "https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEUIMA-32235,https://uima.apache.org/security_report#CVE-2017-15691"  -sie -u

echo "Importing CVE-2008-1728 (522 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2008-1728 -r https://github.com/igniterealtime/Openfire -e c9cd1e521673ef0cccb8795b78d3cbaefb8a576a  -sie -u

echo "Importing CVE-2016-2510 (523 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-2510 -r https://github.com/beanshell/beanshell -e 7c68fde2d6fc65e362f20863d868c112a90a9b49,1ccc66bb693d4e46a34a904db8eeff07808d2ced  -sie -u

echo "Importing CVE-2018-1999046 (524 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1999046 -r https://github.com/jenkinsci/jenkins -e 6867e4469525d16319b1bae9c840b933fe4e23c4  -sie -u

echo "Importing CVE-2017-9805 (525 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9805 -r https://github.com/apache/struts -e 19494718865f2fb7da5ea363de3822f87fbda26:master,6dd6e5cfb7b5e020abffe7e8091bd63fe97c10a:support-2-3  -descr "Possible Remote Code Execution attack when using the Struts REST plugin with XStream handler to handle XML payloads." -links "https://cwiki.apache.org/confluence/display/WW/S2-052"  -sie -u

echo "Importing CVE-2017-1000398 (526 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000398 -r https://github.com/jenkinsci/jenkins/ -e da06fd471cea79123821c778228eeb08e1cedcc7  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32185,https://jenkins.io/security/advisory/2017-10-11/"  -sie -u

echo "Importing CVE-2018-15761 (527 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-15761 -r https://github.com/cloudfoundry/uaa/ -e 3f0730a015d10166de23b7e036743c185f0576a6,95b7d9e7fae534a362b98de1df5bf501cd52c481  -links "https://www.cloudfoundry.org/blog/cve-2018-15761/"  -sie -u

echo "Importing CVE-2017-5641 (528 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-5641 -r https://github.com/apache/flex-blazeds/ -e f861f0993c35e664906609cad275e45a71e2aaf1  -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-5641,https://issues.apache.org/jira/browse/FLEX-35290,https://www.kb.cert.org/vuls/id/307983,https://ossindex.net/resource/package/7103354225/vulnerabilities"  -sie -u

echo "Importing CVE-2019-1003009 (529 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-1003009 -r https://github.com/jenkinsci/active-directory-plugin/ -e 520faf5bb1078d75e5fed10b7bf5ac6241fe2fc4  -descr "An improper certificate validation vulnerability exists in Jenkins Active Directory Plugin 2.10 and earlier in src/main/java/hudson/plugins/active_directory/ActiveDirectoryDomain.java, src/main/java/hudson/plugins/active_directory/ActiveDirectorySecurityRealm.java, src/main/java/hudson/plugins/active_directory/ActiveDirectoryUnixAuthenticationProvider.java that allows attackers to impersonate the Active Directory server Jenkins connects to for authentication if Jenkins is configured to use StartTLS." -links "https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-1003009,https://jenkins.io/security/advisory/2019-01-28/#SECURITY-859"  -sie -u

echo "Importing CVE-2015-1775 (530 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-1775 -r https://github.com/apache/ambari -e 3ab123a109f6384f019db455f256520f4a8b85dd  -sie -u

echo "Importing CVE-2018-15758 (531 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-15758 -r https://github.com/spring-projects/spring-security-oauth/ -e ddd65cd9417ae1e4a69e4193a622300db38e2ef:2.1.3,f92223afc71687bd3156298054903f50aa71fbf:2.2.3,4082ec7ae3d39198a47b5c803ccb20dacefb0b0:2.3.4,623776689fdcc8047f5a908c71f348e1f172a97:2.0.16  -descr "Privilege Escalation in spring-security-oauth2. Spring Security OAuth, versions 2.3 prior to 2.3.4, and 2.2 prior to 2.2.3, and 2.1 prior to 2.1.3, and 2.0 prior to 2.0.16, and older unsupported versions could be susceptible to a privilege escalation under certain conditions. A malicious user or attacker can craft a request to the approval endpoint that can modify the previously saved authorization request and lead to a privilege escalation on the subsequent approval. This scenario can happen if the application is configured to use a custom approval endpoint that declares AuthorizationRequest as a controller method argument.This vulnerability exposes applications that meet all of the following requirements:- Act in the role of an Authorization Server (e.g. @EnableAuthorizationServer)- Use a custom Approval Endpoint that declares AuthorizationRequest as a controller method argumentThis vulnerability does not expose applications that:- Act in the role of an Authorization Server and use the default Approval Endpoint- Act in the role of a Resource Server only (e.g. @EnableResourceServer)- Act in the role of a Client only (e.g. @EnableOAuthClient)Affected Pivotal Products and Versions:Spring Security OAuth 2.3 to 2.3.3Spring Security OAuth 2.2 to 2.2.2Spring Security OAuth 2.1 to 2.1.2Spring Security OAuth 2.0 to 2.0.15Older unsupported versions are also affectedMitigationUsers of affected versions should apply the following mitigation:2.3.x users should upgrade to 2.3.42.2.x users should upgrade to 2.2.32.1.x users should upgrade to 2.1.32.0.x users should upgrade to 2.0.16Older versions should upgrade to a supported branchThere are no other mitigation steps required.History2018-10-16: Initial vulnerability report published." -links "https://pivotal.io/security/cve-2018-15758"  -sie -u

echo "Importing HADOOP-14833 (532 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b HADOOP-14833 -r https://github.com/apache/hadoop/ -e 87f63b6479330840e9d708a729355948bb91fd4d  -descr "" -links "http://hadoop.apache.org/docs/r3.2.0/hadoop-project-dist/hadoop-common/release/3.2.0/RELEASENOTES.3.2.0.html,http://hadoop.apache.org/docs/r3.2.0/hadoop-project-dist/hadoop-common/release/3.2.0/CHANGELOG.3.2.0.html,https://issues.apache.org/jira/browse/HADOOP-14833"  -sie -u

echo "Importing CVE-2017-1000486 (533 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000486 -r https://github.com/primefaces/primefaces/ -e 26e44eb7962cbdb6aa2f47eca0f230f3274358f0  -links "https://snyk.io/vuln/SNYK-JAVA-ORGPRIMEFACES-32045,https://cryptosense.com/blog/weak-encryption-flaw-in-primefaces,https://www.exploit-db.com/exploits/43733,https://blog.mindedsecurity.com/2016/02/rce-in-oracle-netbeans-opensource.html,https://github.com/primefaces/primefaces/issues/1152"  -sie -u

echo "Importing APACHE-AXIS2-5846 (534 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b APACHE-AXIS2-5846 -r https://github.com/apache/axis2-java -e 65aaacc779530682887bc6da4099b5ec4cfab406  -descr "org.apache.axis2:axis2 is a Web Services / SOAP / WSDL engine, the successor to Apache Axis SOAP stack. Affected versions of the package are vulnerable to Local File Inclusion (LFI). Remediation: Upgrade axis2 to version 1.7.5 or higher." -links "https://snyk.io/vuln/SNYK-JAVA-COMSPARKJAVA-31646,https://issues.apache.org/jira/browse/AXIS2-5846,https://svn.apache.org/viewvc?view=revision&revision=1792353"  -sie -u

echo "Importing CVE-2013-6448 (535 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2013-6448 -r https://github.com/seam2/jboss-seam -e 090aa6252affc978a96c388e3fc2c1c2688d9bb5  -sie -u

echo "Importing CVE-2019-3772 (536 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2019-3772 -r https://github.com/spring-projects/spring-integration/ -e 59c69ed40d3755ef59f80872e0ea711adbb13620  -links "https://pivotal.io/security/cve-2019-3772,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKINTEGRATION-73517,https://snyk.io/vuln/SNYK-JAVA-ORGSPRINGFRAMEWORKINTEGRATION-73518"  -sie -u

echo "Importing CVE-2016-0734 (537 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-0734 -r https://github.com/apache/activemq -e 24ad36778534c5ac888f880837075449169578ad,028a33ea7d73fabe6161defffdbfc85578328a68  -descr "The web-based administration console in Apache ActiveMQ 5.x before 5.13.2 does not send an X-Frame-Options HTTP header, which makes it easier for remote attackers to conduct clickjacking attacks via a crafted web page that contains a (1) FRAME or (2) IFRAME element. https://issues.apache.org/jira/browse/AMQ-6170" -sie -u

echo "Importing CVE-2017-1000504 (538 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-1000504 -r https://github.com/jenkinsci/jenkins/ -e ccc374a7176d7704941fb494589790b7673efe2:master,9b39411b1ae07ce8bf6c7df457bde1c6dabba9f:2.95,eec0188cc45d75fd519a5d831b54781ac801dac:2.89.2  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJENKINSCIMAIN-32172,https://jenkins.io/security/advisory/2017-12-14/"  -sie -u

echo "Importing CVE-2017-9804 (539 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2017-9804 -r https://github.com/apache/struts -e 8a04e80f01350c90f053d71366d5e0c2186fded:master,418a20c0594f23764fe29ced400c1219239899a:master,744c1f409d983641af3e8e3b573c2f2d2c2c6d9:support-2-3,a05259ed69a5a48379aa91650e4cd1cb4bd6e5a:master,9d47af6ffa355977b5acc713e6d1f25fac260a2:master,3fddfb6eb562d597c935084e9e81d43ed6bcd02:support-2-3  -descr "A regular expression Denial of Service when using URLValidator." -links "https://cwiki.apache.org/confluence/display/WW/S2-050"  -sie -u

echo "Importing CVE-2018-1298 (540 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1298 -r https://github.com/apache/qpid-broker-j -e 4b9fb37abbe882193b16595ed7b8e9d8383f59e1,30ca170c42c400b41340a81c6a69d33aa19bf189,de509dd955229a395c086a7cca874dc55306648a  -sie -u

echo "Importing CVE-2016-6795 (541 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2016-6795 -r https://github.com/apache/struts -e 030ffa33543f8953306ed0c0dc815c7fb74d7129,8e67b9144aa643769b261e2492cb561e04d016ab  -descr "It is possible to prepare a special URL which will be used for path traversal and execution of arbitrary code on server side. Upgrade to Apache Struts version 2.3.31 when you are using Struts 2.3.20 - 2.3.30 with the Convention plugin." -links "https://cwiki.apache.org/confluence/display/WW/S2-042"  -sie -u

echo "Importing CVE-2018-1062 (542 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1062 -r https://gerrit.ovirt.org/ovirt-engine -e 820888c4e8dfbe79dc55e1ba8e72edb0ebd8890:master,d0e33ace71b7603450fc1aa7725f53dbc545831:ovirt-engine-4.1  -sie -u

echo "Importing CVE-2015-7521 (543 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2015-7521 -r https://github.com/apache/hive -e 98f933f269e6b528ef84912b3d701ca3272ec04b  -sie -u

echo "Importing CVE-2018-1000008 (544 out of 544)"
java -Dvulas.shared.backend.serviceUrl=$1 -jar patch-analyzer-jar-with-dependencies.jar  -b CVE-2018-1000008 -r https://github.com/jenkinsci/pmd-plugin -e f88399a021c22e30cb8fbac5200471d69f1b6224  -links "https://snyk.io/vuln/SNYK-JAVA-ORGJVNETHUDSONPLUGINS-32170,https://jenkins.io/security/advisory/2018-01-22/"  -sie -u
