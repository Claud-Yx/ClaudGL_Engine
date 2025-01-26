#pragma once

class GEngine
{
private:
	static std::shared_ptr<GEngine> kInstance;

private:
	GEngine() = default;

public:
	static std::shared_ptr<GEngine> Generate();

};

