# Import check. NO function is called.
require "json/jwt"
puts "modul=json/jwt yuklendi; surum=#{Gem.loaded_specs['json-jwt'].version}"
puts "sembol JSON::JWT.decode #{JSON::JWT.respond_to?(:decode)}"
puts "sinif JSON::JWS #{defined?(JSON::JWS) ? 'var' : 'yok'}"
