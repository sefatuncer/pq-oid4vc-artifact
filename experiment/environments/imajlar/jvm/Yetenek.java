// Ortam yeteneği (imza doğrulama DEĞİL): JCA sağlayıcılarının kayıtlı imza algoritma adlarında ML-DSA var mı?
import java.security.Provider;
import java.security.Security;
public class Yetenek {
    public static void main(String[] a) {
        for (Provider p : Security.getProviders())
            for (Provider.Service s : p.getServices())
                if (s.getType().equals("Signature") && s.getAlgorithm().toUpperCase().contains("ML-DSA"))
                    System.out.println("SURUM JCA " + p.getName() + " Signature " + s.getAlgorithm());
    }
}
