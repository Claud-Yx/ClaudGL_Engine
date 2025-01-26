#include "pch.h"
#include "EngineCore.h"

std::shared_ptr<GEngine> GEngine::Generate()
{
	if ( !kInstance )
	{
		kInstance = std::make_shared<GEngine>();
	}

	return kInstance;
}
