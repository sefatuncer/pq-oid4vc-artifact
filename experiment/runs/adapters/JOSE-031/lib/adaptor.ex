# JOSE-031 guardian 2.5.0 adaptörü (doğrulamayı erlang-jose 1.11.12'ye devreder: JOSE.JWT.verify_strict).
# Belgeli genel API: Guardian.decode_and_verify(mod, token, %{}, secret: jwk, allowed_algos: W)
# (guardian/token/jwt.ex "allowed_algos", "secret" seçenekleri; decode_token L328-343). Eşleme: MAPPING.md.
# Ortak iskelet (C3 sözleşmesi 1.0 / KOSUCU §1–§3) aynı dosyadadır; doğrulama döngüsü YOK. Ağ erişimi yok.

defmodule A10.Guardian do
  use Guardian, otp_app: :adaptor, issuer: "a10-adaptor"
  def subject_for_token(_r, _c), do: {:ok, "a10"}
  def resource_from_claims(c), do: {:ok, c}
end

defmodule A10.Ortak do
  @x_kol %{"kontrol-EdDSA" => "EdDSA", "kontrol-Ed25519" => "Ed25519", "kontrol-ES384" => "ES384",
           "tedavi-ML-DSA-65" => "ML-DSA-65", "tedavi-composite" => "ML-DSA-65-ES256"}

  def b64d(s), do: Base.url_decode64!(s, padding: false)

  def vektor_yolu(dosya) do
    adaylar = ["/v/" <> dosya, "/v/" <> String.replace_prefix(dosya, "v1.3/", "")]
    Enum.find(adaylar, hd(adaylar), &File.exists?/1)
  end

  # Manifestten YALNIZ dogrulama_girdileri okunur; `insa` ve diğer alanlar okunmaz (yürütücü 01.10).
  def manifest do
    case :persistent_term.get(:a10_manifest, nil) do
      nil ->
        y = Enum.find(["/v/MANIFEST.json", "/v/v1.3/MANIFEST.json"], &File.exists?/1)
        m = y |> File.read!() |> JSON.decode!()
        idx = Map.new(m["vektorler"], fn e -> {e["id"], e["dogrulama_girdileri"] || %{}} end)
        :persistent_term.put(:a10_manifest, idx)
        idx
      idx -> idx
    end
  end

  def jwks(goreli) do
    ("/anahtarlar/" <> String.replace_prefix(goreli, "anahtarlar/", "")) |> File.read!() |> JSON.decode!()
  end

  # Politika → {taban, W | nil, R}. YONTEM.md §2; VARSAYILAN = sözleşme §5.2 L5.
  def politika(is, kutuphane) do
    taban = is["politika"] |> String.split("|") |> hd() |> String.split("@") |> hd()  # ekler yalnız oracle'ı böler
    x = @x_kol[is["kol"]]
    gx = fn -> x || raise "kol icin X tanimsiz" end
    case taban do
      t when t in ["GEC", "P0", "P1", "P2"] -> {taban, kutuphane, []}
      "VARSAYILAN" -> {taban, nil, []}
      "IZIN-A" -> {taban, ["ES256"], []}
      "IZIN-AX" -> {taban, ["ES256", gx.()], []}
      t when t in ["L4", "L4-S", "L4-Y", "L4-YOL"] -> {taban, ["ES256", gx.()], [gx.()]}
      _ -> raise "bilinmeyen politika #{is["politika"]}"
    end
  end

  # Tek imzalı nesnede R ≠ ∅ ise etkin izin listesi R'dir (tek imza R'yi ancak kendisi X ise karşılar; R ⊆ W).
  def tek_imza_izin({_, nil, _}), do: nil
  def tek_imza_izin({_, w, []}), do: w
  def tek_imza_izin({_, _, r}), do: r

  # Anahtar seçimi (sözleşme §8 m.1): başlık kid → vektörün JWKS'i; yoksa alg_kid[alg]; yoksa tek kid. DPoP: başlık jwk.
  def jwk_sec(baslik, dg) do
    cond do
      dg["anahtar"] == "jwk basligindan" -> {baslik["jwk"], "jwk-basligi"}
      dg["jwks"] == nil -> {nil, "JWK"}
      true ->
        ak = if is_binary(dg["alg_kid"]), do: JSON.decode!(dg["alg_kid"]), else: dg["alg_kid"]
        kid = baslik["kid"] || (is_map(ak) && ak[baslik["alg"]]) ||
                (match?([_], dg["kid"] || []) && hd(dg["kid"])) || nil
        {Enum.find(jwks(dg["jwks"])["keys"], &(&1["kid"] == kid)), "JWK"}
    end
  end

  def kosu_adi(cikti) do
    case System.get_env("KOSU") do
      k when is_binary(k) and k != "" -> k
      _ ->
        p = cikti |> Path.basename(".jsonl") |> String.split(".")
        if length(p) >= 2, do: List.last(p), else: "oncesi"
    end
  end

  defp sabit(ad), do: (case File.read("/opt/a/" <> ad) do {:ok, s} -> String.trim(s); _ -> "" end)

  def kos([girdi, cikti | _], dogrula) do
    kosu = kosu_adi(cikti)
    {:ok, out} = File.open(cikti, [:write, :utf8])
    girdi |> File.stream!() |> Stream.map(&String.trim/1) |> Stream.reject(&(&1 == "")) |> Enum.each(fn l ->
      is = JSON.decode!(l)
      t0 = System.monotonic_time(:millisecond)
      gorev = Task.async(fn ->
        try do dogrula.(is) rescue e -> %{sonuc_ham: "istisna", hata_sinifi: "adaptor-hatasi", hata_ozeti: Exception.message(e), api_yolu: nil} end
      end)
      s = case Task.yield(gorev, 60_000) || Task.shutdown(gorev) do
        {:ok, r} -> r
        _ -> %{sonuc_ham: "zaman-asimi", hata_sinifi: "zaman-asimi", hata_ozeti: "60 s asildi", api_yolu: nil}
      end
      ozet = s[:hata_ozeti] && String.slice(to_string(s[:hata_ozeti]), 0, 200)
      satir = %{"sozlesme" => "adaptor-sozlesme/1.0", "hedef_id" => System.get_env("HEDEF_ID", "bilinmiyor"),
        "hedef_surum" => sabit("HEDEF_SURUM"), "adaptor_sha256" => sabit("ADAPTOR_SHA256"), "kosu" => kosu,
        "vektor_id" => is["vektor_id"], "politika" => is["politika"], "kol" => is["kol"],
        "sonuc_ham" => s.sonuc_ham, "hata_sinifi" => s[:hata_sinifi], "hata_ozeti" => ozet,
        "dogrulanan_algoritmalar" => s[:dogrulanan] || [], "api_yolu" => s[:api_yolu],
        "anahtar_yolu" => s[:anahtar_yolu], "sure_ms" => System.monotonic_time(:millisecond) - t0}
      IO.write(out, JSON.encode!(satir) <> "\n")
    end)
    File.close(out)
  end
end

defmodule A10.Adaptor do
  alias A10.Ortak
  # Bataryadaki algoritmalardan yerel destek (jose_jws.erl from_map: ES*, EdDSA/Ed25519/Ed448, HS, PS, RS; ML-DSA yok)
  @kutuphane ["ES256", "ES384", "EdDSA", "Ed25519", "Ed448"]
  @api "Guardian.decode_and_verify(A10.Guardian, jwt, %{}, secret: JOSE.JWK.from_map(jwk), allowed_algos: W)"

  def b6, do: %{sonuc_ham: "uygulanamaz", hata_sinifi: "bicim-desteklenmiyor", hata_ozeti: "B6: MAPPING.md (API incelemesi)", api_yolu: @api}

  # Guardian, verify_strict'in {false, _, _} sonucunu ve yakalanan istisnaları tek bir :invalid_token'a indirger
  # (jwt.ex L336-342). İzin dışı alg ile imza hatası ayrımı başlık alg'ı ve W ile yapılır.
  defp sinifla(:invalid_token, alg, izin) do
    cond do
      alg not in @kutuphane -> "alg-desteklenmiyor"
      izin != nil and alg not in izin -> "alg-izin-disi"
      true -> "imza-gecersiz"
    end
  end
  defp sinifla(r, _alg, _izin) when r in [:token_expired, :token_not_yet_valid], do: "zaman"
  defp sinifla(:secret_not_found, _, _), do: "anahtar-bulunamadi"
  defp sinifla(_, _, _), do: "istisna-diger"

  def dogrula(is) do
    taban = is["politika"] |> String.split("|") |> hd() |> String.split("@") |> hd()
    cond do
      is["serilestirme"] != "compact" -> b6()
      taban == "L4-YOL" ->
        %{sonuc_ham: "ifade-edilemedi", hata_ozeti: "x5c/x5chain yol sinifi politikasi (L4-YOL, B2) icin belgeli API yok", api_yolu: @api}
      true -> dogrula_kompakt(is)
    end
  end

  defp dogrula_kompakt(is) do
    if false do
      b6()
    else
      dg = Ortak.manifest()[is["vektor_id"]] || raise "manifestte yok"
      jwt = is["dosya"] |> Ortak.vektor_yolu() |> File.read!() |> String.trim()
      pol = Ortak.politika(is, @kutuphane)
      izin = Ortak.tek_imza_izin(pol)
      baslik = try do jwt |> String.split(".") |> hd() |> Ortak.b64d() |> JSON.decode!() rescue _ -> %{} end
      alg = baslik["alg"]
      {jwk, yol} = Ortak.jwk_sec(baslik, dg)
      api = if izin == nil, do: String.replace(@api, ", allowed_algos: W", ""), else: @api
      anahtar = try do jwk && JOSE.JWK.from_map(jwk) rescue e -> {:hata, Exception.message(e)} end
      case anahtar do
        {:hata, m} -> %{sonuc_ham: "red", hata_sinifi: "alg-desteklenmiyor", hata_ozeti: "JOSE.JWK.from_map: " <> m, api_yolu: api, anahtar_yolu: yol}
        nil -> %{sonuc_ham: "red", hata_sinifi: "anahtar-bulunamadi", hata_ozeti: "JWK secilemedi", api_yolu: api, anahtar_yolu: yol}
        k ->
          opts = [secret: k] ++ if(izin, do: [allowed_algos: izin], else: [])
          case Guardian.decode_and_verify(A10.Guardian, jwt, %{}, opts) do
            {:ok, _claims} -> %{sonuc_ham: "kabul", api_yolu: api, anahtar_yolu: yol, dogrulanan: []}
            {:error, %{} = e} when is_exception(e) ->
              %{sonuc_ham: "istisna", hata_sinifi: "istisna-diger", hata_ozeti: Exception.message(e), api_yolu: api, anahtar_yolu: yol}
            {:error, r} ->
              %{sonuc_ham: "red", hata_sinifi: sinifla(r, alg, izin), hata_ozeti: "{:error, #{inspect(r)}}", api_yolu: api, anahtar_yolu: yol}
          end
      end
    end
  end

  def main(args), do: Ortak.kos(args, &dogrula/1)
end
