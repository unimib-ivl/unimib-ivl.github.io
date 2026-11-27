# frozen_string_literal: true

# Redirects from old addresses, defined once in _data/redirects.yml (list of {from, to}).
#  - writes /_redirects for Netlify (HTTP 301; "!" also applies when a file exists at the old path);
#  - for page addresses (ending in "/") writes <from>index.html, a page that redirects at once (any host,
#    including GitHub Pages, which has no server-side redirects).
# Addresses of files (e.g. /download/x.zip) on GitHub Pages are handled by the script in _pages/404.md.
module IvlRedirects
  class Generator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      redirects = site.data["redirects"] || []
      lines = redirects.map do |r|
        path, query = r["from"].split("?", 2)
        params = query ? "  #{query.split('&').join(' ')}" : "" # Netlify: query parameters as "key=value" fields
        "#{path}#{params}  #{absolute(site, r['to'])}  301!"
      end
      netlify = Jekyll::PageWithoutAFile.new(site, site.source, "", "_redirects")
      netlify.content = "# Generated from _data/redirects.yml by _plugins/ivl_redirects.rb\n#{lines.join("\n")}\n"
      netlify.data["layout"] = nil
      netlify.data["sitemap"] = false
      site.pages << netlify

      redirects.each do |r|
        next unless r["from"].end_with?("/") && !r["from"].include?("?")

        page = Jekyll::PageWithoutAFile.new(site, site.source, r["from"].sub(%r{^/}, ""), "index.html")
        page.data["layout"] = "redirect"
        page.data["redirect_to"] = r["to"]
        page.data["sitemap"] = false
        page.data["title"] = "Redirecting"
        site.pages << page
      end
    end

    private

    def absolute(site, to)
      to.include?("://") ? to : "#{site.config['baseurl']}#{to}"
    end
  end
end
