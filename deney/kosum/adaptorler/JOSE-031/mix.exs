defmodule A10.MixProject do
  use Mix.Project
  # guardian 2.5.0 (+ erlang-jose 1.11.12) — mix.lock = deney/ortam/hedefler/JOSE-031/cikti/mix.lock (Hex sağlama toplamları)
  def project, do: [app: :adaptor, version: "0.1.0", elixir: "~> 1.20", deps: [{:guardian, "== 2.5.0"}]]
  def application, do: [extra_applications: [:logger, :crypto]]
end
