# Changelog


## [1.7.0](https://github.com/juanjogeyer/simplex2/compare/v1.6.0...v1.7.0) (2025-11-13)


### Features

* add GitHub Actions workflow for publishing Docker images ([e25fe5e](https://github.com/juanjogeyer/simplex2/commit/e25fe5ed9707c4b22296e5321124e9211956a8ee))

## [1.6.0](https://github.com/juanjogeyer/simplex2/compare/v1.5.1...v1.6.0) (2025-11-13)


### Features

* add Dockerfile for Python FastAPI application ([4eced63](https://github.com/juanjogeyer/simplex2/commit/4eced63007161c28e9912dd8a3b5a3595b074e1a))

## [1.5.1](https://github.com/juanjogeyer/simplex2/compare/v1.5.0...v1.5.1) (2025-11-13)


### Bug Fixes

* ensure issues permission is correctly set in release workflow ([60ea185](https://github.com/juanjogeyer/simplex2/commit/60ea185052800c76a37de52906bfaa87b2fa892a))
* remove unnecessary steps from release workflow and update prueba1.py ([3c02509](https://github.com/juanjogeyer/simplex2/commit/3c0250953b830ef5230a2ca2aa396c3899926020))
* update actions versions in release workflow ([d6ec601](https://github.com/juanjogeyer/simplex2/commit/d6ec6013138dc95b001927dc82ede4258d866c96))
* update token in release workflow to use RELEASE_PLEASE_TOKEN ([b7125b5](https://github.com/juanjogeyer/simplex2/commit/b7125b5a58decfe0ca63ebc6a16d46f5edd72d3e))

## [1.4.2](https://github.com/juanjogeyer/simplex2/compare/v1.4.1...v1.4.2) (2025-11-13)


### Bug Fixes

* add repository checkout step before auto-merging Release PR ([4d7aa0f](https://github.com/juanjogeyer/simplex2/commit/4d7aa0f525c7222901bcb92ca0424cc5e57de5bb))

## [1.4.1](https://github.com/juanjogeyer/simplex2/compare/v1.4.0...v1.4.1) (2025-11-13)


### Bug Fixes

* refine auto-merge condition for Release PRs in workflow ([6a2ae62](https://github.com/juanjogeyer/simplex2/commit/6a2ae62988e4831ca3fa1b271b5f06126f56d85f))

## [1.4.0](https://github.com/juanjogeyer/simplex2/compare/v1.3.0...v1.4.0) (2025-11-13)


### Features

* add auto-merge functionality for Release PRs in workflow ([fa95ee3](https://github.com/juanjogeyer/simplex2/commit/fa95ee31d56b9d9fe4396b684f5566e0a7ff5d25))


### Bug Fixes

* replace auto-merge action with GitHub CLI command for Release PRs ([cfffffd](https://github.com/juanjogeyer/simplex2/commit/cfffffddc1615d5824605860147e49b735853f63))
* simplify auto-merge condition for Release PRs in workflow ([a0307e9](https://github.com/juanjogeyer/simplex2/commit/a0307e9bcbf2171bdc8c6a61a697b141cb44bba3))
* update auto-merge action to version 4 in release workflow ([6e4b9a2](https://github.com/juanjogeyer/simplex2/commit/6e4b9a24687f5a89e5e2c7b6c7975bd6cb6a068b))

## [1.3.0](https://github.com/juanjogeyer/simplex2/compare/v1.2.0...v1.3.0) (2025-11-12)


### Features

* enable automatic merging in release-please workflow ([008c1e0](https://github.com/juanjogeyer/simplex2/commit/008c1e0283cddc25a172168fd87543f2f390a1c1))

## [1.2.0](https://github.com/juanjogeyer/simplex2/compare/v1.1.0...v1.2.0) (2025-11-12)


### Features

* add HTML and JavaScript for Simplex Solver tables interface ([f8b0211](https://github.com/juanjogeyer/simplex2/commit/f8b02112871516ef4615a16858c8cfc4813c0124))
* add initial implementation of Simplex Solver with HTML, CSS, and JavaScript ([0c974b6](https://github.com/juanjogeyer/simplex2/commit/0c974b661130ca5051642943a6a8b81e62e0276d))

## [1.1.0](https://github.com/juanjogeyer/simplex2/compare/v1.0.0...v1.1.0) (2025-11-12)


### Features

* add simplex router and service integration for solving optimization problems ([e720ee7](https://github.com/juanjogeyer/simplex2/commit/e720ee7e2df9810960bee9c4b7b5442b0d35126a))
* agregar simplex_service ([2d8ecc4](https://github.com/juanjogeyer/simplex2/commit/2d8ecc493b4f1f8a7ea299d72d101d1a2fc6cbb3))


### Bug Fixes

* enhance test output verbosity and capture during execution ([c858224](https://github.com/juanjogeyer/simplex2/commit/c858224d99a374a2fd6e85fe1a6f2aacefd664c8))
* streamline dependency installation in release workflow ([2265c73](https://github.com/juanjogeyer/simplex2/commit/2265c73e91fd4ce93b2da2f1f57069270055cc21))
* update dependency installation and add pytest configuration ([b4d4df5](https://github.com/juanjogeyer/simplex2/commit/b4d4df5eea5ffca93b57581a47d82b947336efbd))
* update pyproject.toml to correct setuptools package finding configuration ([54a6bdd](https://github.com/juanjogeyer/simplex2/commit/54a6bdd1a360d066a4db254147221ab8c1bd603d))
* update test command to run without verbosity and capture options ([11f9f71](https://github.com/juanjogeyer/simplex2/commit/11f9f7117ac2d89134ebe8640542f7b5a3585b55))
