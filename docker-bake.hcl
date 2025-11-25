variable "REGISTRY" {
  default = "docker.io"
}

variable "VERSION" {
  default = "dev"
}

variable "PYTHON_VERSION" {
  default = "3.10"
}

variable "INSTALLED_SOLC_VERSIONS" {
  default = "0.8.19"
}

function "myth2-tags" {
  params = [NAME]
  result = formatlist("${REGISTRY}/${NAME}:%s", split(",", VERSION))
}

group "default" {
  targets = ["myth2", "myth2-smoke-test"]
}

target "_myth2-base" {
  target = "myth2"
  args = {
    PYTHON_VERSION = PYTHON_VERSION
    INSTALLED_SOLC_VERSIONS = INSTALLED_SOLC_VERSIONS
  }
  platforms = [
    "linux/amd64",
    "linux/arm64"
  ]
}

target "myth2" {
  inherits = ["_myth2-base"]
  tags = myth2-tags("mythril2/myth2")
}

target "myth2-dev" {
  inherits = ["_myth2-base"]
  tags = myth2-tags("mythril2/myth2-dev")
}

target "myth2-smoke-test" {
  inherits = ["_myth2-base"]
  target = "myth2-smoke-test"
  output = ["build/docker/smoke-test"]
}
