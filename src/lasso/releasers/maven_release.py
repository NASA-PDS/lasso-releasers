"""Maven release automation."""
import fnmatch
import os.path
import sys

from lxml import etree

from .release import release_publication

SNAPSHOT_TAG_SUFFIX = "SNAPSHOT"

_mime_types = {
    ".tar.gz": "application/gzip",
    ".zip": "application/zip",
    ".jar": "application/java-archive",
}


def maven_get_version(workspace=None):
    """Get the maven version out of the ``workspace``."""
    # read current version
    workspace = workspace or os.environ.get("GITHUB_WORKSPACE")
    pom_path = os.path.join(workspace, "pom.xml")
    pom_doc = etree.parse(pom_path)
    r = pom_doc.xpath(
        "/pom:project/pom:version",
        namespaces={"pom": "http://maven.apache.org/POM/4.0.0"},
    )
    version = r[0].text
    print(f"Yo yo maven gets version {version} from the pom", file=sys.stderr)
    return version


def maven_upload_assets(repo_name, tag_name, release):
    """Upload packages produced by maven."""
    print(f"Yo yo maven upload assets for {repo_name} and tag {tag_name}", file=sys.stderr)
    # upload assets
    assets_found = False
    assets, workspace = ["*-bin.tar.gz", "*-bin.zip", "*.jar"], os.environ.get("GITHUB_WORKSPACE")
    for dirname, _subdirs, files in os.walk(workspace):
        if dirname.endswith("target"):
            for extension in assets:
                for filename in fnmatch.filter(files, extension):
                    assets_found = True
                    with open(os.path.join(dirname, filename), "rb") as f_asset:
                        release.upload_asset(_mime_types[os.path.splitext(filename)[1]], filename, f_asset)
    if not assets_found:
        raise RuntimeError(f"‼️ No assets found in {workspace}! Aborting!")


def main():
    """Entrypoint."""
    release_publication(SNAPSHOT_TAG_SUFFIX, maven_get_version, maven_upload_assets)


if __name__ == "__main__":
    main()
