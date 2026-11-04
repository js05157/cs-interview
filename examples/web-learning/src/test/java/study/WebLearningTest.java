package study;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;
import org.apache.tomcat.util.descriptor.web.*;
import org.junit.jupiter.api.*;
import java.io.IOException;
import java.net.*;
import java.net.http.*;
import java.nio.file.*;
import static org.junit.jupiter.api.Assertions.*;

class WebLearningTest {
    static Tomcat tomcat; static String base;
    @BeforeAll static void start() throws Exception {
        tomcat = new Tomcat();
        tomcat.setBaseDir(Path.of("target/runtime").toAbsolutePath().toString());
        tomcat.setPort(0); tomcat.getConnector().setProperty("address", "127.0.0.1");
        Context context = tomcat.addWebapp("/learn", Path.of("src/main/webapp").toAbsolutePath().toString());
        context.setParentClassLoader(WebLearningTest.class.getClassLoader());
        Tomcat.addServlet(context,"add",new AddServlet()); context.addServletMappingDecoded("/add","add");
        Tomcat.addServlet(context,"members",new LessonServlet()); context.addServletMappingDecoded("/members","members");
        Tomcat.addServlet(context,"auth",new SessionServlet()); context.addServletMappingDecoded("/auth/*","auth");
        Tomcat.addServlet(context,"cookie",new CookieServlet()); context.addServletMappingDecoded("/cookie/*","cookie");
        Tomcat.addServlet(context,"semantics",new HttpServlet() {
            @Override protected void doGet(HttpServletRequest req,HttpServletResponse resp) throws IOException,ServletException {
                req.getRequestDispatcher("/WEB-INF/views/semantics.jsp").forward(req,resp);
            }
        }); context.addServletMappingDecoded("/semantics","semantics");
        FilterDef filter=new FilterDef(); filter.setFilterName("trace"); filter.setFilter(new TraceFilter());
        context.addFilterDef(filter);
        FilterMap mapping=new FilterMap(); mapping.setFilterName("trace"); mapping.addURLPattern("/*"); mapping.setDispatcher("REQUEST");context.addFilterMap(mapping);
        tomcat.start(); base="http://127.0.0.1:"+tomcat.getConnector().getLocalPort()+"/learn";
    }
    @AfterAll static void stop() throws Exception { if(tomcat!=null){tomcat.stop();tomcat.destroy();} }
    static HttpClient client(){return HttpClient.newBuilder().cookieHandler(new CookieManager(null,CookiePolicy.ACCEPT_ALL)).followRedirects(HttpClient.Redirect.NEVER).build();}
    static HttpResponse<String> get(HttpClient c,String path)throws Exception{return c.send(HttpRequest.newBuilder(URI.create(base+path)).GET().build(),HttpResponse.BodyHandlers.ofString());}
    static HttpResponse<String> post(HttpClient c,String path,String body)throws Exception{return c.send(HttpRequest.newBuilder(URI.create(base+path)).header("Content-Type","application/x-www-form-urlencoded;charset=UTF-8").POST(HttpRequest.BodyPublishers.ofString(body)).build(),HttpResponse.BodyHandlers.ofString());}
    @Test void addsAndRejectsInvalidInput() throws Exception {
        HttpClient c=client();assertEquals("5",get(c,"/add?a=2&b=3").body());
        assertEquals(400,get(c,"/add?a=no&b=3").statusCode());
        assertEquals(400,get(c,"/add?a=2147483647&b=1").statusCode());
        assertEquals(405,post(c,"/add","a=2&b=3").statusCode());
    }
    @Test void appliesRequestFilter()throws Exception {assertEquals("applied",get(client(),"/add?a=2&b=3").headers().firstValue("X-Learning-Filter").orElseThrow());}
    @Test void forwardCompilesJspAndRendersJstlSafely()throws Exception {
        var r=get(client(),"/members");assertEquals(200,r.statusCode());
        assertTrue(r.body().contains("요청에서 전달한 값"));assertTrue(r.body().contains("1. Ada"));
        assertTrue(r.body().contains("&lt;script&gt;demo&lt;/script&gt;"));assertFalse(r.body().contains("<script>demo</script>"));
    }
    @Test void elScopeCoercionAndRemoveAllScopes()throws Exception {
        String body=get(client(),"/semantics").body();assertTrue(body.contains("before=P, request=R, sum=3"));assertTrue(body.contains("after=true"));
    }
    @Test void webInfIsPrivateAndCustom404KeepsStatus()throws Exception {
        var r=get(client(),"/WEB-INF/views/members.jsp");assertEquals(404,r.statusCode());assertTrue(r.body().contains("요청한 페이지를 찾을 수 없습니다."));
    }
    @Test void cookieOnlyComesBackOnNextRequestAndCanBeDeleted()throws Exception {
        HttpClient c=client();var first=get(c,"/cookie/set");assertEquals("absent",first.body());
        String header=first.headers().firstValue("Set-Cookie").orElseThrow();assertTrue(header.contains("HttpOnly"));assertTrue(header.contains("SameSite=Lax"));assertTrue(header.contains("Path=/learn"));
        assertEquals("4",get(c,"/cookie/check").body());get(c,"/cookie/delete");assertEquals("absent",get(c,"/cookie/check").body());
    }
    @Test void loginUsesPrgAndLogoutInvalidatesSession()throws Exception {
        HttpClient c=client();assertEquals(401,get(c,"/auth/profile").statusCode());
        var login=post(c,"/auth/login","user=learner&password=demo-only");assertEquals(303,login.statusCode());assertEquals("/learn/auth/profile",login.headers().firstValue("Location").orElseThrow());
        assertEquals("learner",get(c,"/auth/profile").body());assertEquals(303,post(c,"/auth/logout","").statusCode());assertEquals(401,get(c,"/auth/profile").statusCode());
    }
    @Test void rejectsWrongPasswordWithoutLoggingIn()throws Exception {HttpClient c=client();assertEquals(401,post(c,"/auth/login","user=learner&password=wrong").statusCode());assertEquals(401,get(c,"/auth/profile").statusCode());}
}
