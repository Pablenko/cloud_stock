import setuptools

setuptools.setup(
    name="cloud_trading",
    version="0.1",
    description="The package contains alfa version of cloud trading platform",
    author="Pawel Przybylski",
    author_email="pawel.przybylski91@gmail.com",
    license="MIT",
    packages=setuptools.find_packages(),
    package_data={"": ["*.json"]},
    entry_points={
        "console_scripts": [
            "trading_cloud_producer=producer.kafka_producer:main",
            "trading_cloud_engine=engine.kafka_consumer:main",
        ]
    },
)
