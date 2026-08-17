import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { GqlContextType, GqlExecutionContext } from '@nestjs/graphql';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
	private readonly logger: Logger = new Logger();

	public intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
		const arrivalTime = Date.now();
		const requestType = context.getType<GqlContextType>();

		if (requestType === 'http') {
			/* Develop if needed */
		} else if (requestType === 'graphql') {
			/* (1) Print Request */
			const gqlContex = GqlExecutionContext.create(context);
			this.logger.log(`${this.stringify(gqlContex.getContext().req.body)}`, 'REQUEST');

			/* (2) Error Hnadling with GraphQL */

			/* (3) No error is giving Response below */
			return next.handle().pipe(
				tap((context) => {
					const responseTime = Date.now() - arrivalTime;
					this.logger.log(`${this.stringify(context)} - ${responseTime}ms \n\n`, 'RESPONSE');
				}),
			);
		}
		return next.handle();
	}

	private stringify(context: ExecutionContext): string {
		return JSON.stringify(context).slice(0, 75);
	}
}
