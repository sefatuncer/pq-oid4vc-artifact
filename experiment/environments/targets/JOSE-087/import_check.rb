# Import check: the gem is loaded and the presence of the API symbols is written. NO function is called.
require "jwt"
puts "modul=jwt (ruby-jwt) yuklendi; surum=#{JWT.gem_version}"
puts "sembol JWT.decode #{JWT.respond_to?(:decode)}"
puts "sabit JWT::JWA #{defined?(JWT::JWA) ? 'var' : 'yok'}"
