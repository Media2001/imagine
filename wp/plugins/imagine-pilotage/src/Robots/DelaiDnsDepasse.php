<?php

declare(strict_types=1);

namespace Imagine\Pilotage\Robots;

/** L'adaptateur DNS peut également lever cette exception à son échéance. */
final class DelaiDnsDepasse extends \RuntimeException
{
}
