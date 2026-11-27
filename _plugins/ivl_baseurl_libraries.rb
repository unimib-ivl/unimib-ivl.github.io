# frozen_string_literal: true

# Self-hosted libraries are listed in _config.yml (third_party_libraries) with addresses such as
# "/assets/vendor/...", which the theme prints as they are. When the site is built under a sub-path
# (e.g. https://<owner>.github.io/<repo>/, before the custom domain is set), prefix them with the baseurl.
# With an empty baseurl (site at the root of its domain) nothing changes.
module IvlBaseurlLibraries
  def self.prefix(value, base)
    case value
    when Hash then value.transform_values { |v| prefix(v, base) }
    when Array then value.map { |v| prefix(v, base) }
    when String
      value.start_with?("/") && !value.start_with?("//") && !value.start_with?("#{base}/") ? "#{base}#{value}" : value
    else value
    end
  end
end

Jekyll::Hooks.register :site, :after_init do |site|
  base = site.config["baseurl"].to_s.chomp("/")
  libraries = site.config["third_party_libraries"]
  next if base.empty? || !libraries.is_a?(Hash)

  libraries.each_value do |library|
    library["url"] = IvlBaseurlLibraries.prefix(library["url"], base) if library.is_a?(Hash) && library["url"]
  end
end
