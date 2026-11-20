<?php

declare(strict_types=1);

namespace Imagine\Connecteur\Tests;

use Imagine\Connecteur\Event;
use Imagine\Connecteur\NamedRule;
use Imagine\Connecteur\Validator;
use PHPUnit\Framework\TestCase;

final class ValidationTest extends TestCase
{
    public function testBillingRulesIdentifyEachAnomalyWithoutLeakingValues(): void
    {
        $validator = Validator::billing(['fiction']);
        self::assertSame([], $validator->validate(EventTest::event()));
        $cases = [
            ['identity', ['name' => ''], 'identity'],
            ['address', ['street' => '1 rue Fiction'], 'address'],
            ['total_minor', 1201, 'amounts'],
            ['total_minor', 12.0, 'amounts'],
            ['lines', [['product' => 'Produit fictif', 'amount_minor' => PHP_INT_MAX],
                ['product' => 'Produit fictif', 'amount_minor' => 1]], 'amounts'],
            ['lines', [], 'amounts'],
            ['currency', '', 'amounts'],
            ['payment_method', 'unknown-fiction', 'payment_method'],
            ['enterprise_number', '0123456789', 'enterprise_number'],
        ];
        foreach ($cases as [$field, $value, $rule]) {
            $event = EventTest::event();
            $content = $event->content;
            $content[$field] = $value;
            $invalid = new Event($event->type, $event->sourceId, $event->occurredAt, $content);
            $violations = $validator->validate($invalid);
            self::assertContains($rule, array_column($violations, 'rule'));
            self::assertNotEmpty($violations[0]->message);
        }
    }

    public function testEnterpriseValidatorAndNewRulesAreInjectedWithoutChangingEngine(): void
    {
        $event = EventTest::event();
        $content = $event->content + ['enterprise_number' => 'fiction-valid'];
        $event = new Event($event->type, $event->sourceId, $event->occurredAt, $content);
        $validator = Validator::billing(['fiction'], static fn (string $number): bool => $number === 'fiction-valid');
        self::assertSame([], $validator->validate($event));
        $extended = $validator->with(new NamedRule(
            'step_extra',
            static fn (Event $event): ?string => 'Contrôle fictif.'
        ));
        self::assertSame('step_extra', $extended->validate($event)[0]->rule);
        self::assertSame([], $validator->validate($event), 'The original rule set stays immutable.');
    }
}
