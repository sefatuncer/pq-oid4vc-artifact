# İçe aktarma kontrolü: gem yüklenir, API sembollerinin varlığı yazılır. Hiçbir işlev ÇAĞRILMAZ.
require "jwt"
puts "modul=jwt (ruby-jwt) yuklendi; surum=#{JWT.gem_version}"
puts "sembol JWT.decode #{JWT.respond_to?(:decode)}"
puts "sabit JWT::JWA #{defined?(JWT::JWA) ? 'var' : 'yok'}"
